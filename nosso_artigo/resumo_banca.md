# Resumo para a banca — Benchmark, código e abordagem

> Baseado no código (`experiments/drone_routing.py`, `plot_results.py`, `analyze_review.py`),
> nas instâncias e nos CSVs de resultado. O artigo é usado apenas como referência.

---

## 1. O benchmark de origem: E-VRPTW (Schneider/Goeke)

Partimos do conjunto de instâncias do **Electric Vehicle Routing Problem with Time Windows (E-VRPTW)**
de Schneider et al. (2014), na versão de dados de Goeke (2019). Ele é derivado das clássicas
instâncias de Solomon do VRPTW.

**O que cada instância contém** (formato em `data/raw/evrptw/instances/evrptw_instances/c101C5.txt`):

- Um **depósito** único (`Type = d`);
- **Estações de recarga** (`Type = f`) — incluindo uma estação na posição do próprio depósito;
- **Clientes** (`Type = c`) com coordenadas `(x, y)`, **demanda**, **janela de tempo**
  `[ReadyTime, DueDate]` e **tempo de serviço**;
- Parâmetros globais de energia: capacidade de bateria `Q`, capacidade de carga `C`,
  taxa de consumo `r`, taxa inversa de recarga `g` e velocidade `v`.

**Tamanho usado:** 92 instâncias — **36 pequenas** (5, 10 ou 15 clientes) e **56 grandes**
(100 clientes). O parser (`parse_instance`) lê cada arquivo, separa depósito/estações/clientes
e ordena os clientes por índice. Distâncias são **euclidianas** (`distance`).

---

## 2. O que modificamos no benchmark

O E-VRPTW original é **mono-período** e assume infraestrutura **fixa e disponível desde o início**.
Nós o reinterpretamos como um problema multi-período de drones (que chamamos **PRMD-ER**):

| Aspecto | Original E-VRPTW | Nossa reinterpretação |
|---|---|---|
| Veículo | Veículo elétrico terrestre | Drone (margem energética mais apertada) |
| Horizonte | 1 período | **H = 4 períodos** |
| Clientes | Todos ativos | Crescem por período: `C_t ⊆ C_{t+1}`, `|C_t| = ⌈|C|·t/H⌉` |
| Estações | Todas fixas | **3 políticas** de disponibilização: `depot`, `phased` (gradual), `all` (completa) |
| Energia | Parâmetros `Q,r,g` da instância | Bateria própria do drone **medida em distância** (`B=80`) |
| Janelas / autonomia | Restrições rígidas | **Restrições flexíveis** (penalidades); só capacidade de carga é rígida |

Pontos importantes para ser transparente com a banca:

- A **ativação de clientes** (`active_customers`) usa ordenação **angular** em torno do depósito
  (cenário `spatial`, default) — simula a área atendida crescendo por setores.
- A **seleção gradual de estações** (`select_stations`) é **gulosa**: a cada estação adicionada,
  escolhe a que mais reduz a soma das distâncias dos clientes ativos à estação mais próxima.
  Esse **acoplamento demanda↔infraestrutura** é o que não existe no E-VRPTW puro.
- Usamos parâmetros próprios do drone (`DroneParams`: capacidade 50, `B=80`, velocidade 1,
  recarga com custo fixo + proporcional) em vez dos `Q/C/r/g` nativos da instância — os campos
  da instância são lidos, mas a energética é a do drone. Isso é uma escolha deliberada de
  modelagem e está listada como limitação no artigo.

---

## 3. Pipeline do código (`run_experiment`)

Para cada instância → cada período (1..4) → cada política de estação → cada algoritmo:

1. **Ativa clientes** do período (`active_customers`);
2. **Seleciona estações** disponíveis (`select_stations`);
3. **Constrói rotas** (`build_routes`) — passando a solução do período anterior como
   *warm start* (herança), via `route_history`;
4. **Avalia** (`evaluate`) e grava métricas + tempo de execução.

Saída: `results.csv` (linha a linha) + três sumários agregados (`summary.csv`,
`station_policy_summary.csv`, `algorithm_station_summary.csv`).

---

## 4. Função objetivo e avaliação (`evaluate`)

A avaliação **simula** cada rota: percorre os vértices, acumula tempo, atualiza bateria e,
quando um arco excede a autonomia, tenta inserir **uma** parada de recarga (`insert_recharge`)
— a estação ativa que minimiza o desvio `d_if + d_fj − d_ij`. Se nenhuma estação resolve,
o arco é contado como **inviável**.

```
F = D + α·A + γ·R + β·I
```

com **distância** `D`, **atraso** `A` (α=10), **nº de rotas** `R` (γ=100) e **trechos inviáveis**
`I` (β=10⁶). O β é deliberadamente dominante: uma solução com trecho energeticamente inviável
nunca deve "ganhar" de uma viável só por ter menos distância. Janelas são **soft** (espera se
chega cedo; penaliza atraso); capacidade de carga é **hard**.

---

## 5. Os 9 algoritmos comparados (`build_routes`)

Todos produzem **só a sequência de clientes**; as recargas são reconstruídas pelo módulo de
reparo compartilhado — isso torna a comparação justa.

- **Construtivos:** `EDD` (ordena por fim da janela), `Sweep` (ângulo polar),
  `Nearest` (vizinho mais próximo guloso);
- **GRASP:** construção gulosa-randomizada (lista restrita de 3) + 2-opt, com 20 *restarts*;
- **ALNS** (`alns_routes`): a referência. 3 operadores de destruição (aleatória, pior,
  por relação espacial), 2 de reparo (guloso e *regret-2*), aceitação por *simulated annealing*
  e pesos adaptativos pelo esquema-σ de Ropke & Pisinger;
- **MP-EAVNS** (método principal) + **3 variantes de ablação** (sem herança, sem perturbação,
  sem 2-opt auxiliar).

### MP-EAVNS — `energy_aware_vns`

É uma **Variable Neighborhood Search sensível à energia e multi-período**:

1. **Sementes:** melhor entre herança (período anterior) + EDD + Sweep + Nearest +
   construções randomizadas do GRASP;
2. **5 vizinhanças** encadeadas (*first-improvement*): `N1` 2-opt intra-rota, `N2` realocação,
   `N3` troca, `N4` divisão de rota, `N5` união de rotas;
3. **Reparo energético** embutido na avaliação;
4. **Perturbação (`shake`)** quando estagna — forçada após 4 iterações sem melhora;
   até `k_max = 80` iterações;
5. **Herança entre períodos** (`warm_start_routes`): copia rotas do período anterior,
   remove clientes inativos e insere os novos na posição de menor aumento marginal.

---

## 6. Resultados principais (B=80, 9.936 execuções)

- **Viabilidade:** MP-EAVNS atinge **100%** sob política Completa e **98,6%** sob Gradual
  (empata com ALNS); construtivos ficam abaixo de 52%.
- **Qualidade da rota (só viáveis):** MP-EAVNS produz rotas **6,7% mais curtas que ALNS**
  (Completa) e 6,2% (Gradual).
- **Objetivo penalizado:** 36% menor que GRASP; 8,4% acima da ALNS no agregado — mas essa
  diferença vem **só do regime Depósito** (sem estações); restringindo a Gradual+Completa,
  MP-EAVNS fica até 0,7% abaixo da ALNS.
- **Achado central:** a disponibilização **gradual** recupera quase todo o benefício —
  distância viável apenas **1,4% acima** da Completa.
- **Custo:** MP-EAVNS ~3,7s/solução vs. ~14,4s da ALNS (≈4× mais rápida) e ~0,35s do GRASP.
- **Ablação:** a **herança** é o componente mais crítico (removê-la piora o objetivo ~20%);
  2-opt auxiliar e perturbação têm efeito pequeno (<1%).

---

## 7. Perguntas esperadas da banca + respostas

**1. Por que reutilizar o E-VRPTW em vez de criar instâncias próprias?**
Porque é um benchmark consolidado, derivado de Solomon, amplamente usado e com depósito,
clientes, janelas, demandas e estações já validados. Isso dá comparabilidade e
reprodutibilidade. A literatura de UAV+recarga frequentemente improvisa instâncias derivadas
de Solomon justamente por falta de benchmark padronizado — nós aproveitamos um existente e só
adicionamos a dimensão multi-período.

**2. Vocês usaram os parâmetros de energia das instâncias (Q, r, g)?**
Não diretamente. Lemos esses campos, mas adotamos um modelo energético próprio do drone, com
**bateria medida em unidades de distância** (`B=80`) e consumo proporcional à distância. É uma
simplificação deliberada — consistente com a natureza geométrica do E-VRPTW — e está declarada
como limitação. Não modela carga, vento, altitude nem pouso/decolagem.

**3. Por que tratar autonomia e janelas como penalidades, e não como restrições rígidas?**
Para distinguir **inviabilidade estrutural** (a infraestrutura não basta) de **inviabilidade
algorítmica** (a busca não encontrou solução viável apesar da infraestrutura). Com restrições
rígidas, soluções parcialmente inviáveis seriam simplesmente descartadas e não conseguiríamos
medir *o quão perto* da viabilidade cada método chega. A capacidade de carga, por outro lado,
é fácil de respeitar sempre, então fica rígida.

**4. O peso β = 10⁶ não distorce a análise?**
Ele domina o objetivo de propósito: garante que nenhuma solução inviável vença uma viável. Por
isso reportamos as métricas **separadas** — taxa de viabilidade e distância **restrita a
soluções viáveis** — neutralizando β e isolando o desempenho puro de roteamento. As conclusões
de qualidade vêm dessas métricas, não do objetivo agregado.

**5. Qual a diferença real entre MP-EAVNS e ALNS, já que a ALNS é mais conhecida?**
São filosofias diferentes: ALNS usa **destruição-reconstrução** adaptativa em grandes
vizinhanças; a MP-EAVNS alterna **5 vizinhanças locais estruturadas** + perturbação. No nosso
problema elas empatam em viabilidade, mas a MP-EAVNS gera rotas viáveis ~6,7% mais curtas e é
~4× mais rápida. A vantagem vem sobretudo da **herança entre períodos**, que dá um ponto de
partida muito melhor nas instâncias grandes (vence 88,8% dos pares).

**6. A comparação de tempo é justa, se ALNS e MP-EAVNS têm operadores diferentes?**
Igualamos o **número de iterações** (`k_max = 80`), não o tempo de CPU. Reportamos os dois: sob
mesmo orçamento de iterações, a MP-EAVNS ainda sai mais rápida e com rotas melhores.
Reconhecemos que comparação por CPU seria outra leitura — está como nota no texto.

**7. Por que a ablação "sem herança" piora tanto e as outras quase nada?**
Porque a herança transporta estrutura útil entre períodos consecutivos — sem ela, cada período
recomeça do zero (Nearest) e perde a otimização acumulada, sobretudo nos períodos finais com
mais clientes. Já o 2-opt auxiliar é redundante com a vizinhança `N1`, e a perturbação
raramente é acionada quando as 5 vizinhanças já esgotaram as melhorias.

**8. Por que o reparo energético insere só uma estação por arco?**
É uma decisão de custo computacional e de design: o reparo é **guloso por arco**, minimizando o
desvio local. Arcos que exigiriam duas ou mais recargas são marcados como inviáveis. Nos
experimentos com `B≥80` sob política Completa isso nunca impede a viabilidade (I=0 em todas as
execuções), então a simplificação não compromete os resultados no regime de interesse.

**9. Como sabem que o ganho não é só ruído estatístico?**
Fizemos comparação **pareada** MP-EAVNS×ALNS em soluções viáveis sob Completa: vantagem média
de 76,9 unidades de distância com IC 95% [65,4; 88,4] — intervalo que não cruza zero. Nas
pequenas há empate técnico (esperado, poucos clientes); o ganho real está nas grandes.

**10. O cenário "gradual" é realista?**
Sim — é a motivação do trabalho. Uma rede de entrega por drones cresce gradualmente: novos
clientes e novas estações entram com o tempo. A pergunta prática é "quanto desempenho dá pra
preservar antes da infraestrutura total estar pronta", e a resposta foi: quase tudo (98,6% de
viabilidade, distância só 1,4% pior que a infraestrutura completa).
