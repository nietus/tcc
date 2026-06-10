# Plano metodológico do artigo

## Problema

Nome de trabalho: **PRMD-ER - Problema de Roteamento Multi-Período de Drones com Estações de Recarga**.

A ideia central é estudar uma operação de entrega por drones que cresce em períodos. Em cada período entram mais clientes, e a infraestrutura de recarga pode seguir três políticas: apenas depósito, ativação gradual ou todas as estações disponíveis.

## Método principal recomendado

O método principal é a **MP-EAVNS - Multi-Period Energy-Aware Variable Neighborhood Search**, com construção randomizada, herança da solução do período anterior, busca local e reparo energético.

A VNS/ALNS é a opção mais adequada para o TCC neste momento porque:

- é forte e aceita em problemas de roteamento;
- permite explicar claramente cada vizinhança;
- lida bem com restrições de recarga, capacidade e janelas de tempo;
- aproveita o GRASP atual como construção inicial;
- é mais controlável que uma abordagem memética completa.

Um algoritmo memético pode entrar depois como comparação, mas não deve ser o primeiro método principal. Ele exigiria representação cromossômica, operadores de cruzamento, reparo energético e muito ajuste paramétrico antes de gerar resultado defensável.

## Representação da solução

Cada solução armazena, por período:

- sequência de clientes por rota;
- política de estações ativa no período;
- estações de recarga reconstruídas por um módulo de reparo.

As estações não devem ser tratadas como genes fixos da rota no início. É melhor reconstruí-las durante a avaliação, porque isso deixa a busca local focar na ordem dos clientes e evita muitas soluções artificialmente diferentes.

## Avaliação

A função objetivo deve combinar:

- distância total;
- atraso total;
- número de drones/rotas;
- número de recargas;
- penalidade por trecho energeticamente inviável.

Nas tabelas finais, as soluções principais devem ter zero trechos inviáveis sempre que possível. A penalidade continua útil durante o desenvolvimento, pois permite comparar soluções parcialmente reparadas sem quebrar o experimento.

## Vizinhanças implementadas

Ordem usada na implementação atual:

1. **2-opt intra-rota** para reduzir distância.
2. **Relocate intra/inter-rota** para mover um cliente.
3. **Swap intra/inter-rota** para trocar dois clientes.
4. **Split route** para quebrar rotas energeticamente ruins.
5. **Merge route** para reduzir frota quando houver folga.
6. **Energy repair** para inserir estações com menor aumento de distância.

O próximo operador estrutural é o **Station activation swap**, que testa outra estação no cenário gradual.

## Estratégia multi-período

O período seguinte já é inicializado com a solução do período anterior, adicionando apenas os novos clientes antes da VNS. Isso imita uma operação real em expansão e diferencia o trabalho de um E-VRPTW comum resolvido separadamente em cada período.

## Experimentos

Experimentos mínimos para o artigo:

- 12 instâncias pequenas para desenvolvimento e testes rápidos;
- 36 instâncias pequenas para comparação completa já executada;
- instâncias de 100 clientes para escalabilidade;
- autonomias 60, 80 e 100 já executadas;
- políticas de estação: depósito, gradual, completa e gradual otimizada;
- algoritmos: EDD, Sweep, Nearest, GRASP e MP-EAVNS já executados; ALNS completa entra como próxima comparação.

## Gráficos

Gráficos prioritários:

- objetivo médio por algoritmo;
- trechos inviáveis por algoritmo;
- objetivo médio por política de estações;
- trechos inviáveis por política de estações;
- objetivo por período;
- mapa de rotas de uma instância representativa;
- linha do tempo de ativação de estações.

Os gráficos principais já são gerados por `experiments/plot_results.py`.

