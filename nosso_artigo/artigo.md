
\documentclass[12pt]{article}

\usepackage{sbc-template}
\usepackage{graphicx,url}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazil]{babel}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{array}
\usepackage{indentfirst}
\usepackage{xcolor}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,calc,shapes.geometric,shapes.symbols,backgrounds}

\definecolor{algA}{HTML}{CBD5E1}
\definecolor{algB}{HTML}{94A3B8}
\definecolor{algC}{HTML}{64748B}
\definecolor{algD}{HTML}{0E7490}
\definecolor{algE}{HTML}{0C4A6E}
\definecolor{polA}{HTML}{BBF7D0}
\definecolor{polB}{HTML}{34D399}
\definecolor{polC}{HTML}{047857}
\definecolor{accent}{HTML}{B45309}
\definecolor{neutral}{HTML}{111827}

\sloppy

\title{Roteamento Multi-Período de Drones com Janelas de Tempo e Disponibilização Gradual de Estações de Recarga}

\author{Antonio S. C. Neto\inst{1}, Zenilton K. G. do Patrocínio\inst{1}}

\address{Pontifícia Universidade Católica de Minas Gerais (PUC Minas)
\email{\{antonio.couto, zenilton\}@pucminas.br}
}

\begin{document}

\maketitle

\begin{abstract}
This paper studies a multi-period extension of the Electric Vehicle Routing Problem with Time Windows (E-VRPTW) for drone delivery under gradual station deployment. Demand and external charging stations are activated over successive periods, and routes are evaluated by distance, tardiness and energy-infeasibility penalties. The proposed MP-EAVNS is an energy-aware Variable Neighborhood Search that combines local search, energy repair and warm starts from previous periods. In 9{,}936 runs over 92 instances, MP-EAVNS reaches 100\,\% viable solutions under full station availability and 98.6\,\% under gradual deployment. Under full availability, it produces viable routes 6.7\,\% shorter than an adapted ALNS (Adaptive Large Neighborhood Search) and 9.6\,\% shorter than GRASP (Greedy Randomized Adaptive Search Procedure); under gradual deployment, its viable-route distance is only 1.4\,\% above full availability. The results suggest that gradual station activation can preserve most of the routing benefit of full availability.
\end{abstract}

\begin{resumo}
Este artigo estuda uma extensão multi-período do Problema de Roteamento de Veículos Elétricos com Janelas de Tempo (E-VRPTW) para entregas por drones com disponibilização gradual de estações de recarga. A demanda e as estações externas tornam-se disponíveis progressivamente, e as rotas são avaliadas por distância, atraso e penalidades de inviabilidade energética. A MP-EAVNS proposta é uma Busca em Vizinhança Variável sensível à energia que combina busca local, reparo energético e inicialização herdada entre períodos. Em 9.936 execuções sobre 92 instâncias, a MP-EAVNS atinge 100\,\% de soluções viáveis sob disponibilidade completa de estações e 98,6\,\% sob disponibilidade gradual. Na política completa, produz rotas viáveis 6,7\,\% mais curtas que uma ALNS adaptada (Busca Adaptativa em Grande Vizinhança) e 9,6\,\% mais curtas que um GRASP (\textit{Greedy Randomized Adaptive Search Procedure}); na política gradual, sua distância viável fica apenas 1,4\,\% acima da disponibilidade completa. Os resultados indicam que a disponibilização gradual da infraestrutura pode preservar boa parte do benefício da disponibilidade total.
\end{resumo}

\section{Introdução} \label{sec:introducao}

Problemas de roteamento formam uma das bases da otimização combinatória aplicada à logística. O Problema de Roteamento de Veículos (\textit{Vehicle Routing Problem}, VRP) \cite{dantzig1959truck} generaliza a decisão de construir rotas para uma frota, enquanto o VRP com Janelas de Tempo (\textit{VRP with Time Windows}, VRPTW) \cite{solomon1987algorithms} incorpora compromissos entre custo espacial e nível de serviço. Outras extensões, como o Problema de Coleta e Entrega (\textit{Pickup and Delivery Problem}, PDP) \cite{savelsbergh1995general,li2001metaheuristic} e o roteamento dinâmico \cite{psaraftis1988dynamic,berbeglia2010dynamic,pillac2013review}, mostram que restrições temporais, decisões sequenciais e operadores de reparo são componentes recorrentes em problemas logísticos reais.

A eletrificação da frota acrescenta uma restrição adicional: a rota só é operacionalmente viável se respeitar a autonomia do veículo e a disponibilidade de recarga. O Problema de Roteamento de Veículos Elétricos com Janelas de Tempo (\textit{Electric Vehicle Routing Problem with Time Windows}, E-VRPTW) \cite{schneider2014evrptw} tornou-se referência para esse cenário ao combinar janelas de tempo, bateria limitada e estações intermediárias; seu conjunto de instâncias \cite{goeke2019evrptwdata} deriva das instâncias de Solomon e é amplamente usado para comparação experimental. Revisões recentes de roteamento verde e veículos elétricos reforçam que infraestrutura de recarga, autonomia e escolha de estações não são apenas detalhes operacionais, mas decisões que afetam diretamente a estrutura das rotas \cite{asghari2021green,ghorbani2020environmentally,stamadianos2023routing}.

Em drones de entrega, essa dependência é ainda mais forte. A autonomia é menor, a capacidade de carga é reduzida e a margem energética tende a ser mais apertada do que em veículos terrestres. Revisões sobre sistemas de entrega por drones destacam autonomia, recarga e pontos de apoio como fatores centrais de planejamento \cite{raivi2023drone}. Trabalhos recentes já estudam veículos aéreos não tripulados (\textit{Unmanned Aerial Vehicles}, UAVs) com janelas de tempo e recarga \cite{shi2023uav}, formulações multiobjetivo para roteamento verde de UAVs \cite{coelho2017green}, localização-roteamento com estações em aplicações industriais \cite{ribeiro2020uav} e roteamento de drones com localização de estações em armazéns \cite{vichitkunakorn2024stocktaking}.

Apesar desses avanços, a maior parte da literatura considera um único horizonte de decisão e assume que a infraestrutura de recarga está fixa e disponível desde o início. Essa hipótese é forte para operações em expansão: uma rede de entregas por drones tende a crescer gradualmente, tanto pela entrada de novos clientes quanto pela disponibilização progressiva de estações externas. Nesse contexto, uma decisão relevante não é apenas qual rota construir com a infraestrutura completa, mas quanto desempenho pode ser preservado antes que toda a infraestrutura esteja disponível.

Este artigo investiga essa questão por meio do Problema de Roteamento Multi-período de Drones com Estações de Recarga (PRMD-ER), uma extensão do E-VRPTW reinterpretada para drones. Em cada período, há um conjunto de clientes ativos $C_t$ e um conjunto de estações externas disponíveis $F_t$; ambos crescem ao longo do horizonte. Três políticas de estações são comparadas: apenas depósito, disponibilidade gradual e disponibilidade completa. As janelas de tempo e a bateria são tratadas como restrições flexíveis, com penalidades explícitas para atraso e inviabilidade energética.

Para resolver o problema, é proposta a MP-EAVNS (\textit{Multi-Period Energy-Aware Variable Neighborhood Search}), uma Busca em Vizinhança Variável (VNS) sensível à energia. O método combina construção randomizada, cinco vizinhanças de clientes, reparo energético por visitas a estações existentes e inicialização herdada entre períodos. A escolha por buscas em vizinhança é coerente com a literatura de roteamento com múltiplas restrições, na qual operadores de vizinhança, destruição-reconstrução e reparo são amplamente usados para lidar com soluções parcialmente inviáveis \cite{ropke2006adaptive,mladenovic1997variable,cai2022variable,zhou2024memetic}.

A contribuição do trabalho é tripla: formalizar um cenário multi-período de entregas por drones com disponibilização gradual de estações, avaliar seu impacto sobre a viabilidade energética e comparar a MP-EAVNS com heurísticas construtivas e metaheurísticas de referência. Os resultados separam objetivo penalizado, viabilidade energética e distância em soluções viáveis, de modo que o efeito da infraestrutura possa ser analisado.

\section{Trabalhos Relacionados} \label{sec:relacionados}

O VRPTW \cite{solomon1987algorithms} é a base clássica para rotas com compromisso entre distância e atendimento dentro de janelas de tempo. O E-VRPTW adotado neste trabalho preserva essa estrutura e acrescenta autonomia limitada e estações de recarga. O PRMD-ER parte dessa base e introduz uma dimensão multi-período, na qual os conjuntos de clientes ativos $C_t$ e de estações disponíveis $F_t$ crescem ao longo do horizonte. Assim, mantém-se a estrutura clássica de atendimento com janelas de tempo, mas a principal dificuldade passa a ser a interação entre crescimento da demanda e disponibilidade energética.

Sob informação parcial e restrições acopladas, métodos exatos perdem tração rapidamente, o que levou a literatura de roteamento a consolidar metaheurísticas baseadas em vizinhanças e reparo. A ALNS \cite{ropke2006adaptive} adapta a escolha de operadores de destruição e reconstrução conforme o desempenho histórico, enquanto a VNS \cite{mladenovic1997variable} alterna vizinhanças distintas para escapar de ótimos locais. Algoritmos meméticos seguem a mesma lógica híbrida: combinam busca populacional com refinamento local especializado, como mostram propostas recentes para PDP com operadores adaptados à precedência \cite{zhou2024memetic}.

A literatura recente de Problemas Dinâmicos de Coleta e Entrega (\textit{Dynamic Pickup and Delivery Problem}, DPDP), sintetizada na revisão de \cite{cai2023survey}, reforça que decisões sequenciais, informação parcial e múltiplas restrições operacionais exigem métodos capazes de corrigir soluções incompletas ou degradadas ao longo da busca. Nesse contexto, aplicações de VNS a variantes práticas do problema \cite{cai2022variable} indicam que alternar vizinhanças estruturais e aplicar operadores de reparo são mecanismos recorrentes em soluções competitivas. O PRMD-ER adota essa linha, mas desloca o foco para viabilidade energética e disponibilização gradual de infraestrutura.

A viabilidade energética, antes ausente do VRP clássico, foi gradualmente incorporada pela literatura de roteamento verde. Revisões do \textit{Green VRP} \cite{asghari2021green} e classificações de variantes ambientalmente amigáveis \cite{ghorbani2020environmentally} cobrem veículos elétricos, recarga e troca de baterias; análises de problemas com veículos elétricos e autônomos \cite{stamadianos2023routing} destacam recarga e infraestrutura como decisões de primeira classe.

Dentro dessa linha, o E-VRPTW \cite{schneider2014evrptw} estabeleceu a referência para roteamento elétrico com janelas de tempo: veículos com bateria limitada atendem clientes e podem visitar estações intermediárias para recarga. O conjunto de instâncias associado \cite{goeke2019evrptwdata} deriva das instâncias de Solomon e inclui clientes, depósito, estações e parâmetros energéticos. O PRMD-ER usa essa base e acrescenta três elementos: períodos com clientes ativos crescentes $C_t$, políticas de disponibilidade de estações $F_t$ e uma avaliação penalizada que separa objetivo, viabilidade energética e distância em soluções viáveis.

Em drones, a margem energética é tipicamente menor do que em veículos elétricos terrestres, o que faz com que problemas reais raramente sejam apenas geométricos. Revisões de sistemas de entrega por drones \cite{raivi2023drone} organizam a literatura em planejamento de trajetória, recarga e segurança, evidenciando que autonomia, recarga e disponibilidade de pontos de apoio afetam diretamente o roteamento.

Sobre esse pano de fundo, diversos trabalhos atacaram o roteamento de UAVs com recarga em variantes específicas. Há estudos com janelas de tempo e recarga resolvidos por busca adaptativa em grandes vizinhanças, com instâncias derivadas de Solomon na ausência de \textit{benchmarks} padronizados \cite{shi2023uav}; formulações multiobjetivo com autonomia limitada e múltiplas estações \cite{coelho2017green}; localização-roteamento de UAVs com estações para inspeção de correias transportadoras na mineração \cite{ribeiro2020uav}, ilustrando a relevância industrial do tema; e combinações de localização de estações com roteamento de drones para inventário em armazéns \cite{vichitkunakorn2024stocktaking}.

Esses trabalhos confirmam a relevância da combinação UAV + recarga + localização, mas todos assumem horizonte único e infraestrutura fixa. A possibilidade de que ela evolua ao longo do tempo, exigindo decisões de roteamento sob essa evolução, é a lacuna que este trabalho aborda.

\section{Metodologia} \label{sec:metodologia}

Esta seção apresenta a formulação do PRMD-ER, as instâncias utilizadas, os algoritmos comparados e o método principal MP-EAVNS. São descritos a entrada de clientes, a disponibilidade de estações, a construção de rotas, o reparo energético e a herança entre períodos.

\subsection{Formulação do Problema} \label{subsec:formulacao}

Seja $G=(V,A)$ um grafo completo euclidiano com vértices $V = \{0\} \cup C \cup F$: depósito $0$, clientes $C$ e estações candidatas $F$. O depósito é único por instância, em conformidade com o \textit{benchmark} E-VRPTW \cite{schneider2014evrptw,goeke2019evrptwdata}. Cada cliente $i$ tem demanda $q_i$, tempo de serviço $s_i$ e janela $[a_i, b_i]$. Cada arco $(i,j)$ tem distância euclidiana $d_{ij}$ e tempo de viagem $d_{ij}/v$, com $v$ a velocidade constante do drone. A frota é homogênea, com capacidade $Q$ e bateria $B$ medida em unidades de distância: o drone parte do depósito ou de uma estação com $B$ unidades e cada arco consome $d_{ij}$. O modelo energético depende apenas da distância --- não de carga, vento, altitude ou fases de pouso/decolagem --- escolha consistente com o \textit{benchmark} E-VRPTW e discutida como limitação na Seção~\ref{sec:conclusao}.

O horizonte é dividido em períodos $T = \{1, \ldots, H\}$. Em cada período $t$, apenas um subconjunto $C_t \subseteq C$ de clientes está ativo e apenas um subconjunto $F_t \subseteq F$ de estações externas está disponível. Os dois conjuntos só crescem ao longo dos períodos: $C_t \subseteq C_{t+1}$ e $F_t \subseteq F_{t+1}$. O conjunto $C_t$ é determinado por ordenação angular crescente em torno do depósito, a partir do eixo horizontal positivo, simulando uma expansão por setores da área atendida; sua cardinalidade é $|C_t|=\lceil |C| \cdot t/H \rceil$. O depósito permanece disponível como ponto de recarga em todos os cenários; as políticas abaixo controlam apenas a disponibilidade das estações externas:

\begin{itemize}
\item Depósito: $F_t = \emptyset$ em todo período, isto é, não há estações externas disponíveis e a recarga intermediária só pode ocorrer no próprio depósito;
\item Gradual: as estações externas são disponibilizadas em $H$ parcelas, sendo $|F_t| = \lceil |F| \cdot t/H \rceil$ a cardinalidade do conjunto externo disponível no período $t$. As estações concretas escolhidas para entrar em $F_t \setminus F_{t-1}$ são selecionadas por uma regra gulosa que minimiza, a cada estação adicionada, a soma das distâncias dos clientes em $C_t$ à estação disponível mais próxima --- isto é, cada nova estação é disponibilizada onde mais aproxima a infraestrutura dos clientes já atendidos no período. Esse acoplamento entre crescimento de demanda e expansão de infraestrutura é uma característica do PRMD-ER que não aparece em variantes E-VRPTW puras;
\item Completa: $F_t = F$ em todo período, ou seja, toda a infraestrutura está disponível desde $t = 1$.
\end{itemize}

Uma solução do período $t$ é um conjunto de rotas $x_t = \{R_1, \ldots, R_m\}$, em que $m=R(x_t)$, que começam e terminam no depósito, atendem cada cliente em $C_t$ exatamente uma vez, podem conter paradas intermediárias no depósito ou em estações de $F_t$, e respeitam a capacidade de carga: para cada rota $R$, $\sum_{i \in R \cap C} q_i \leq Q$. Não há limite superior fixo de frota; novas rotas podem ser abertas, mas são penalizadas por $R(x_t)$ na função objetivo. Denotando por $D(x_t)$ a distância total, $A(x_t)$ o atraso total, $R(x_t)$ o número de rotas e $I(x_t)$ o número de trechos energeticamente inviáveis remanescentes após o reparo, a função objetivo penalizada do período $t$ é:
\begin{equation}
\min \; \mathcal{F}(x_t) \;=\; D(x_t) \;+\; \alpha\, A(x_t) \;+\; \gamma\, R(x_t) \;+\; \beta\, I(x_t)
\label{eq:objetivo}
\end{equation}
com pesos fixados em $\alpha = 10$, $\gamma = 100$ e $\beta = 10^6$. Os valores de $\alpha$ e $\gamma$ são compatíveis com as magnitudes de distância e número de rotas nas instâncias avaliadas. Já $\beta$ é deliberadamente dominante: uma solução com trecho energeticamente inviável não deve dominar soluções viáveis apenas por ter menor distância ou menor atraso.

A função penalizada é usada como escalar único para aceitação de movimentos durante a busca, enquanto a análise final separa seus componentes em objetivo, viabilidade e distância viável. Autonomia, janelas de tempo e número de rotas são, portanto, tratados na função objetivo como termos ponderados, enquanto a capacidade de carga é mantida como restrição rígida. Essa escolha separa dois casos: inviabilidade algorítmica, quando a busca não encontra uma combinação viável apesar da infraestrutura disponível, e inviabilidade estrutural, quando as estações de $F_t$ não bastam para conectar a rota. Como o reparo considera no máximo uma parada intermediária entre dois vértices consecutivos, arcos que exigiriam duas ou mais recargas são classificados como inviáveis. Nos experimentos, esse limite não impede viabilidade sob a política Completa com $B \geq 80$, em que a MP-EAVNS atinge $I(x_t)=0$ em todas as execuções.

Formalmente, o atraso de uma rota é
\begin{equation}
A(R) \;=\; \sum_{i \in R \cap C} \max\!\bigl(0,\; \tau_i(R) - b_i\bigr)
\label{eq:atraso}
\end{equation}
em que $\tau_i(R)$ é o instante de início do serviço em $i$ ao longo de $R$; se a chegada ocorre antes de $a_i$, o drone espera até o início da janela. Denotando por $e(R,i)$ o nível de bateria disponível em $i$ na rota $R$ e por $i^-$ o vértice anterior a $i$ na mesma rota, a atualização de bateria é
\begin{equation}
\begin{aligned}
e(R, i) \; &=\; e(R, i^-) - d_{i^- i} \\
e(R, i^-) \; &=\; B \quad \text{se } i^- \in \{0\}\cup F_t
\end{aligned}
\label{eq:autonomia}
\end{equation}
Na segunda linha, $e(R,i^-)=B$ representa a recarga antes da saída de $i^-$ quando o vértice anterior é o depósito ou uma estação ativa. O arco é energeticamente viável quando $e(R,i)\geq 0$; valores negativos são permitidos na avaliação e penalizados por $I(x_t)$.
A contagem de trechos inviáveis após o reparo é
\begin{equation}
I(x_t) \;=\; \sum_{R \in x_t} \bigl| \{ (i, j) \in R \,:\, e(R, j) < 0 \} \bigr|
\label{eq:inviabilidade}
\end{equation}
em que $(i,j)\in R$ denota um par de vértices consecutivos na sequência da rota.

A Figura~\ref{fig:problem} ilustra um período do PRMD-ER: o drone parte do depósito $0$, visita clientes ativos e usa a estação $f$ como parada intermediária antes de retornar.

\begin{figure}[ht]
\centering
\resizebox{0.55\textwidth}{!}{
\begin{tikzpicture}[
font=\scriptsize,
depot/.style={draw=neutral, line width=0.4pt, rectangle, rounded corners=1pt, fill=algA, minimum size=5mm, inner sep=1pt},
client/.style={circle, draw=neutral, line width=0.3pt, fill=algD!35, minimum size=4.2mm, inner sep=0pt},
station/.style={regular polygon, regular polygon sides=3, draw=neutral, line width=0.3pt, fill=polB, minimum size=4.6mm, inner sep=0pt},
edge/.style={line width=0.7pt, draw=algE, -{Latex[length=1.6mm]}}
]

\node[depot] (d) at (0,0) {$0$};
\node[client] (c1) at (1.5,0.8) {$c_1$};
\node[client] (c2) at (2.9,0.3) {$c_2$};
\node[station] (s) at (4.0,1.0) {$f$};
\node[client] (c3) at (5.3,0.4) {$c_3$};
\node[client] (c4) at (3.7,-0.9) {$c_4$};

\draw[edge] (d) -- (c1);
\draw[edge] (c1) -- (c2);
\draw[edge] (c2) -- (s);
\draw[edge] (s) -- (c3);
\draw[edge] (c3) -- (c4);
\draw[edge, dashed] (c4) -- (d);

\end{tikzpicture}
}
\caption{Um período do PRMD-ER.}
\label{fig:problem}
\end{figure}

\subsection{Reparo Energético} \label{subsec:reparo}

Como a sequência de paradas em estações é determinada por uma decisão geométrica local --- e não como parte da combinatória de clientes --- adota-se um módulo de reparo independente, compartilhado por todos os algoritmos comparados. Ele percorre cada rota da esquerda para a direita simulando $e(R, \cdot)$ conforme a Equação~\eqref{eq:autonomia}. Sempre que um arco $(i, j)$ violaria $e(R,j)\geq 0$, o módulo procura uma estação já ativa $f \in F_t$ como parada intermediária, sob dois critérios cumulativos:
\begin{enumerate}
\item Viabilidade: $e(R, i) \geq d_{if}$ e $B \geq d_{fj}$;
\item Custo mínimo: dentre as $f$ viáveis, escolhe-se a que minimiza $\Delta_{ij}(f) = d_{if} + d_{fj} - d_{ij}$.
\end{enumerate}
Se nenhuma estação satisfaz ambos, o arco permanece inviável e contribui com uma unidade em $I(x_t)$. O trajeto passa por $i \to f \to j$, sem retorno a $i$, e $F$ permanece fixo: o reparo apenas escolhe qual estação já instalada visitar. Essa separação entre roteamento e reparo torna os algoritmos comparáveis, já que todos produzem apenas a sequência de clientes e compartilham o módulo. O reparo é guloso por arco --- minimiza o aumento local sem otimizar conjuntamente todas as paradas da rota.

\subsection{Instâncias e Cenários}

As 92 instâncias do \textit{benchmark} E-VRPTW \cite{schneider2014evrptw,goeke2019evrptwdata} fornecem depósito, clientes, estações, demandas, janelas e tempos de serviço, com distâncias euclidianas. Cada instância é expandida em $H = 4$ períodos, com clientes ativados pela ordenação angular da Seção~\ref{subsec:formulacao}. As 36 instâncias pequenas têm 5, 10 ou 15 clientes; as 56 grandes têm 100. Os experimentos principais fixam $B=80$; a sensibilidade varia $B \in \{60, 80, 100\}$.

\subsection{Algoritmos Comparados} \label{subsec:algoritmos}

A comparação inclui nove algoritmos listados a seguir. Todos produzem apenas a sequência de clientes; as paradas de recarga são reconstruídas pelo módulo da Seção~\ref{subsec:reparo}.

\begin{itemize}
\item EDD (\textit{Earliest Due Date}): ordena clientes pelo fim da janela $b_i$;
\item Sweep (varredura): ordena clientes pelo ângulo polar em relação ao depósito;
\item Nearest (vizinho mais próximo): construção gulosa que escolhe o cliente ainda não atendido mais próximo do último vértice da rota;
\item GRASP (\textit{Greedy Randomized Adaptive Search Procedure}): construção gulosa randomizada por lista restrita seguida de 2-opt, que inverte trechos de uma rota;
\item ALNS: inicializada pela melhor entre Nearest, EDD e Sweep após esse refinamento 2-opt; usa três operadores de destruição (remoção aleatória, do pior e por relação espacial), dois de reparo (guloso e \textit{regret-2}), aceitação por \textit{simulated annealing} \cite{kirkpatrick1983optimization} e pesos atualizados pelo esquema $\sigma$ de \cite{ropke2006adaptive};
\item MP-EAVNS: método principal, descrito a seguir;
\item Variantes da MP-EAVNS, cada uma com um componente desativado: sem herança (reinicializa cada período com a heurística Nearest), sem perturbação (encerra ao estagnar) e sem 2-opt auxiliar (omite chamadas extras de 2-opt; o reparo na avaliação permanece ativo).
\end{itemize}

\subsection{MP-EAVNS} \label{subsec:mpeavns}

A MP-EAVNS estende a VNS clássica \cite{mladenovic1997variable} para o ambiente multi-período com reparo energético. Parte da melhor solução entre EDD, Sweep, Nearest e múltiplas execuções da construção randomizada do GRASP, e explora cinco vizinhanças encadeadas, aceitando apenas movimentos que reduzem $\mathcal{F}$:

\begin{itemize}
\item $\mathcal{N}_1$ -- 2-opt intra-rota: inverte um trecho de uma rota para reduzir distância;
\item $\mathcal{N}_2$ -- realocação: remove um cliente e o reinsere na melhor posição (intra- ou inter-rota);
\item $\mathcal{N}_3$ -- troca: troca dois clientes entre posições (intra- ou inter-rota);
\item $\mathcal{N}_4$ -- divisão: separa em duas uma rota cuja distância acumulada excede a autonomia;
\item $\mathcal{N}_5$ -- união: combina duas rotas curtas quando há folga de bateria e capacidade;
\item $\mathcal{R}_E$ -- reparo energético: durante a avaliação, contabiliza uma parada em uma estação já ativa $f \in F_t$ sempre que o arco $(i,j)$ violar a autonomia, escolhendo a parada que produz o menor aumento de distância $d_{if} + d_{fj} - d_{ij}$.
\end{itemize}

A Figura~\ref{fig:neighborhoods} ilustra cada movimento (linha superior: antes; linha inferior: depois). Quadrados denotam o depósito, círculos clientes, triângulos estações; arestas em laranja marcam arcos modificados.

\begin{figure}[ht]
\centering
\resizebox{0.92\textwidth}{!}{
\begin{tikzpicture}[
font=\tiny,
v/.style={circle, draw=neutral, line width=0.3pt, minimum size=2.2mm, inner sep=0pt, fill=algD!35},
d/.style={rectangle, draw=neutral, line width=0.3pt, minimum size=2.4mm, inner sep=0pt, fill=algA, rounded corners=0.3pt},
s/.style={regular polygon, regular polygon sides=3, draw=neutral, line width=0.3pt, minimum size=2.6mm, inner sep=0pt, fill=polB},
e/.style={line width=0.55pt, draw=algE},
e2/.style={line width=0.7pt, draw=accent},
lbl/.style={font=\scriptsize, text=neutral, anchor=north},
tile/.style={inner sep=2pt}
]

% ---------- N1: 2-opt ----------
\begin{scope}[xshift=0cm, yshift=0cm]
\node[lbl] at (1.2, -0.9) {$\mathcal{N}_1$ -- 2-opt};
\node[d] (n1a0) at (0,0.45) {}; \node[v] (n1a1) at (0.6,0.45) {};
\node[v] (n1a2) at (1.2,0.65) {}; \node[v] (n1a3) at (1.8,0.25) {};
\node[v] (n1a4) at (2.4,0.45) {}; \node[d] (n1a5) at (3.0,0.45) {};
\draw[e] (n1a0) -- (n1a1) -- (n1a2); \draw[e, dashed] (n1a2) -- (n1a3); \draw[e] (n1a3) -- (n1a4) -- (n1a5);
\node[font=\tiny, text=neutral, anchor=west] at (3.1,0.45) {antes};

\node[d] (n1b0) at (0,-0.15) {}; \node[v] (n1b1) at (0.6,-0.15) {};
\node[v] (n1b2) at (1.2,-0.05) {}; \node[v] (n1b3) at (1.8,-0.35) {};
\node[v] (n1b4) at (2.4,-0.15) {}; \node[d] (n1b5) at (3.0,-0.15) {};
\draw[e] (n1b0) -- (n1b1); \draw[e2] (n1b1) -- (n1b3) -- (n1b2) -- (n1b4); \draw[e] (n1b4) -- (n1b5);
\node[font=\tiny, text=neutral, anchor=west] at (3.1,-0.15) {depois};
\end{scope}

% ---------- N2: realocação ----------
\begin{scope}[xshift=4.8cm, yshift=0cm]
\node[lbl] at (1.2, -0.9) {$\mathcal{N}_2$ -- realocação};
\node[d] (n2a0) at (0,0.45) {}; \node[v] (n2a1) at (0.6,0.45) {};
\node[v, fill=accent!50] (n2a2) at (1.2,0.55) {}; \node[v] (n2a3) at (1.8,0.45) {};
\node[v] (n2a4) at (2.4,0.45) {}; \node[d] (n2a5) at (3.0,0.45) {};
\draw[e] (n2a0) -- (n2a1) -- (n2a2) -- (n2a3) -- (n2a4) -- (n2a5);

\node[d] (n2b0) at (0,-0.15) {}; \node[v] (n2b1) at (0.6,-0.15) {};
\node[v] (n2b3) at (1.2,-0.15) {}; \node[v] (n2b4) at (1.8,-0.15) {};
\node[v, fill=accent!50] (n2b2) at (2.4,-0.05) {}; \node[d] (n2b5) at (3.0,-0.15) {};
\draw[e] (n2b0) -- (n2b1) -- (n2b3) -- (n2b4); \draw[e2] (n2b4) -- (n2b2); \draw[e] (n2b2) -- (n2b5);
\end{scope}

% ---------- N3: troca ----------
\begin{scope}[xshift=9.6cm, yshift=0cm]
\node[lbl] at (1.2, -0.9) {$\mathcal{N}_3$ -- troca};
\node[d] (n3a0) at (0,0.45) {}; \node[v, fill=accent!50] (n3a1) at (0.6,0.45) {};
\node[v] (n3a2) at (1.2,0.45) {}; \node[v] (n3a3) at (1.8,0.45) {};
\node[v, fill=polB!60] (n3a4) at (2.4,0.45) {}; \node[d] (n3a5) at (3.0,0.45) {};
\draw[e] (n3a0) -- (n3a1) -- (n3a2) -- (n3a3) -- (n3a4) -- (n3a5);

\node[d] (n3b0) at (0,-0.15) {}; \node[v, fill=polB!60] (n3b4) at (0.6,-0.15) {};
\node[v] (n3b2) at (1.2,-0.15) {}; \node[v] (n3b3) at (1.8,-0.15) {};
\node[v, fill=accent!50] (n3b1) at (2.4,-0.15) {}; \node[d] (n3b5) at (3.0,-0.15) {};
\draw[e] (n3b0) -- (n3b4) -- (n3b2) -- (n3b3) -- (n3b1) -- (n3b5);
\end{scope}

% ---------- N4: divisão ----------
\begin{scope}[xshift=0cm, yshift=-2.6cm]
\node[lbl] at (1.2, -0.9) {$\mathcal{N}_4$ -- divisão};
\node[d] (n4a0) at (0,0.45) {}; \node[v] (n4a1) at (0.6,0.45) {};
\node[v] (n4a2) at (1.2,0.45) {}; \node[v] (n4a3) at (1.8,0.45) {};
\node[v] (n4a4) at (2.4,0.45) {}; \node[d] (n4a5) at (3.0,0.45) {};
\draw[e] (n4a0) -- (n4a1) -- (n4a2) -- (n4a3) -- (n4a4) -- (n4a5);

\node[d] (n4b0) at (0,-0.15) {}; \node[v] (n4b1) at (0.6,-0.15) {};
\node[v] (n4b2) at (1.2,-0.15) {}; \node[d] (n4bd) at (1.5,-0.15) {};
\node[d] (n4bd2) at (1.8,-0.15) {}; \node[v] (n4b3) at (2.1,-0.15) {};
\node[v] (n4b4) at (2.4,-0.15) {}; \node[d] (n4b5) at (3.0,-0.15) {};
\draw[e] (n4b0) -- (n4b1) -- (n4b2) -- (n4bd);
\draw[e2] (n4bd2) -- (n4b3) -- (n4b4) -- (n4b5);
\end{scope}

% ---------- N5: união ----------
\begin{scope}[xshift=4.8cm, yshift=-2.6cm]
\node[lbl] at (1.2, -0.9) {$\mathcal{N}_5$ -- união};
\node[d] (n5a0) at (0,0.45) {}; \node[v] (n5a1) at (0.6,0.45) {};
\node[d] (n5ad) at (1.2,0.45) {}; \node[d] (n5ad2) at (1.5,0.45) {};
\node[v] (n5a2) at (1.8,0.45) {}; \node[v] (n5a3) at (2.4,0.45) {};
\node[d] (n5a5) at (3.0,0.45) {};
\draw[e] (n5a0) -- (n5a1) -- (n5ad);
\draw[e] (n5ad2) -- (n5a2) -- (n5a3) -- (n5a5);

\node[d] (n5b0) at (0,-0.15) {}; \node[v] (n5b1) at (0.6,-0.15) {};
\node[v] (n5b2) at (1.5,-0.15) {}; \node[v] (n5b3) at (2.1,-0.15) {};
\node[v] (n5b4) at (2.4,-0.15) {}; \node[d] (n5b5) at (3.0,-0.15) {};
\draw[e2] (n5b0) -- (n5b1) -- (n5b2) -- (n5b3) -- (n5b4) -- (n5b5);
\end{scope}

% ---------- Reparo energético ----------
\begin{scope}[xshift=9.6cm, yshift=-2.6cm]
\node[lbl] at (1.2, -0.9) {$\mathcal{R}_E$ -- reparo energético};
\node[d] (n6a0) at (0,0.45) {}; \node[v] (n6a1) at (0.7,0.45) {};
\node[v] (n6a2) at (1.5,0.45) {}; \node[v] (n6a3) at (2.3,0.45) {};
\node[d] (n6a5) at (3.0,0.45) {};
\draw[e] (n6a0) -- (n6a1) -- (n6a2);
\draw[e, dashed, draw=accent] (n6a2) -- (n6a3);
\draw[e] (n6a3) -- (n6a5);
\node[font=\tiny, text=accent, anchor=south] at (1.9,0.5) {viola $B$};

\node[d] (n6b0) at (0,-0.15) {}; \node[v] (n6b1) at (0.7,-0.15) {};
\node[v] (n6b2) at (1.4,-0.15) {}; \node[s] (n6bs) at (1.9,-0.05) {};
\node[v] (n6b3) at (2.4,-0.15) {}; \node[d] (n6b5) at (3.0,-0.15) {};
\draw[e] (n6b0) -- (n6b1) -- (n6b2);
\draw[e2] (n6b2) -- (n6bs) -- (n6b3);
\draw[e] (n6b3) -- (n6b5);
\end{scope}

\end{tikzpicture}
}
\caption{Efeito das cinco vizinhanças de clientes e do reparo energético sobre uma rota pequena.}
\label{fig:neighborhoods}
\end{figure}

Quando nenhuma vizinhança melhora a solução corrente, uma perturbação remove e reinsere uma fração dos clientes e a busca continua a partir da melhor solução conhecida. O processo executa até $k_{\max}=80$ iterações principais; uma perturbação é forçada quando a busca local estagna por quatro iterações consecutivas. A Figura~\ref{fig:mpeavns} resume esse fluxo.

\begin{figure}[ht]
\centering
\resizebox{0.88\textwidth}{!}{
\begin{tikzpicture}[
font=\scriptsize,
node distance=8mm and 9mm,
box/.style={draw=neutral, line width=0.45pt, rounded corners=2pt, align=center, minimum width=2.65cm, minimum height=0.82cm, inner sep=4pt},
main/.style={box, fill=algD!20},
repair/.style={box, fill=polB!38},
shake/.style={box, fill=accent!24},
outputbox/.style={box, fill=algE!20},
arrow/.style={-{Latex[length=2.4mm]}, line width=0.8pt, draw=neutral},
back/.style={-{Latex[length=2.4mm]}, line width=0.7pt, dashed, draw=neutral}
]

\node[main] (seed) {Solução inicial};
\node[main, right=of seed] (local) {Busca em\\$\mathcal{N}_1$--$\mathcal{N}_5$};
\node[repair, right=of local] (rep) {Reparo\\energético};
\node[main, right=of rep] (eval) {Aceita se\\melhorar};
\node[shake, below=of rep] (shake) {Perturbação\\se estagnar};
\node[outputbox, right=of eval] (best) {Retorna\\$S_{\text{best}}$};

\draw[arrow] (seed) -- (local);
\draw[arrow] (local) -- (rep);
\draw[arrow] (rep) -- (eval);
\draw[arrow] (eval) -- (best);
\draw[back] (eval.south) |- (shake.east);
\draw[back] (shake.west) -| node[pos=0.28, below, font=\tiny, align=center] {até $k_{\max}$\\iterações} (local.south);

\end{tikzpicture}
}
\caption{Fluxo iterativo da MP-EAVNS.}
\label{fig:mpeavns}
\end{figure}

A lógica multi-período altera apenas o ponto de partida da busca. Dada a melhor solução $x_t^\star$ do período $t$, o período $t+1$ começa por copiar essa solução; as rotas copiadas, porém, não ficam fixas e podem ser modificadas pela busca local subsequente. Cada novo cliente em $C_{t+1} \setminus C_t$ é inserido na posição de menor aumento marginal de distância, abrindo uma nova rota quando necessário.

Depois dessa inserção, o reparo energético é reexecutado com as estações disponíveis em $F_{t+1}$. Assim, a herança preserva estrutura útil entre períodos consecutivos, mas a viabilidade final continua dependendo do reparo e da busca local no período corrente.

\section{Resultados} \label{sec:resultados}

Os experimentos cobrem as 92 instâncias do \textit{benchmark} E-VRPTW reinterpretado, com quatro períodos, três políticas e nove algoritmos --- $92 \times 4 \times 3 \times 9 = 9.936$ execuções, com $B = 80$ fixo. Hardware: Intel Core i7-13650HX (16\,GB de RAM), Windows 11, Python 3.12.10, uma única \textit{thread} por execução.

\subsection{Comparação entre Algoritmos}

A Tabela~\ref{tab:algoritmos} apresenta as métricas médias agregadas sobre as três políticas. Como $\beta=10^6$ na Equação~\eqref{eq:objetivo}, o objetivo penalizado é dominado por trechos inviáveis; por isso a análise também reporta a taxa de viabilidade ($I(x_t)=0$) e, nas tabelas seguintes, distância restrita a soluções viáveis, que isolam o desempenho de roteamento puro.

\begin{table}[ht]
\centering
\caption{Métricas médias por algoritmo ($B=80$).}
\label{tab:algoritmos}
\begin{tabular}{lrrrrr}
\toprule
Algoritmo & Objetivo & Distância & Atraso & Rotas & Inviáveis \\
\midrule
EDD & 8.110.288 & 1.779,5 & 179,5 & 16,42 & 8,11 \\
Sweep & 4.293.766 & 1.303,2 & 1.180,3 & 16,74 & 4,28 \\
Nearest & 3.657.117 & 1.270,6 & 1.490,9 & 14,45 & 3,64 \\
GRASP & 2.525.490 & 1.368,2 & 908,8 & 14,46 & 2,51 \\
ALNS & 1.491.736 & 1.150,6 & 2,3 & 14,32 & 1,49 \\
MP-EAVNS & 1.617.556 & 1.071,0 & 1,7 & 14,31 & 1,62 \\
MP-EAVNS sem 2-opt aux. & 1.630.227 & 1.071,9 & 0,5 & 14,32 & 1,63 \\
MP-EAVNS sem perturb. & 1.632.965 & 1.076,4 & 1,6 & 14,38 & 1,63 \\
MP-EAVNS sem herança & 1.936.032 & 1.174,6 & 45,8 & 14,29 & 1,93 \\
\bottomrule
\end{tabular}
\end{table}

No objetivo penalizado, a MP-EAVNS reduz a média em 36,0\,\% frente ao GRASP e 56--80\,\% frente às construtivas, ficando 8,4\,\% acima da ALNS; esta, por sua vez, reduz o objetivo em 40,9\,\% frente ao GRASP. A leitura agregada é afetada pela política Depósito (limite inferior sem estações externas e muitas inviabilidades estruturais); por isso, a Figura~\ref{fig:algorithm-summary} separa viabilidade por política e compara distância nos regimes com infraestrutura externa, onde ALNS e MP-EAVNS empatam em viabilidade e a MP-EAVNS produz rotas viáveis mais curtas.

\begin{figure}[ht]
\centering
\includegraphics[width=0.82\textwidth]{figures/drone_routing_review/algorithm_summary.pdf}
\caption{Viabilidade por política (a) e distância média entre soluções viáveis nas políticas Gradual e Completa (b), considerando GRASP, ALNS e MP-EAVNS.}
\label{fig:algorithm-summary}
\end{figure}

Quando a agregação é restrita às políticas com infraestrutura externa (Gradual e Completa), o ranking se inverte: a MP-EAVNS apresenta objetivo penalizado 0,7\,\% menor que a ALNS (9.306 contra 9.374). Assim, a vantagem agregada da ALNS na Tabela~\ref{tab:algoritmos} deve ser lida como efeito do regime Depósito, não como superioridade geral de roteamento nos cenários operacionais de interesse.

\subsection{Efeito da Política de Estações}

A Tabela~\ref{tab:estacoes} compara as três políticas agregando todos os algoritmos (Recargas é o número médio de visitas a estações, distinto do $R(x_t)$ penalizado). A Completa funciona como limite superior; a Gradual fica apenas 2,3\,\% acima dela no objetivo e 89,5\,\% abaixo da política Depósito, recuperando quase todo o benefício energético. Distâncias médias de Gradual e Completa são praticamente iguais (1.253,9 vs.\ 1.252,3, +0,1\,\%); a degradação da Gradual aparece mais no atraso (431,9 vs.\ 427,0, +1,1\,\%) e na pequena inviabilidade residual.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.1}
\caption{Métricas médias por política de estações. Cada linha agrega 3.312 execuções ($9$ algoritmos $\times$ $92$ instâncias $\times$ $4$ períodos).}
\label{tab:estacoes}
\begin{tabular}{lrrrrr}
\toprule
Política & Objetivo & Distância & Atraso & Recargas & Inviáveis \\
\midrule
Depósito & 7.423.220 & 1.249,2 & 411,6 & 1,07 & 7,42 \\
Gradual & 779.701 & 1.253,9 & 431,9 & 7,73 & 0,77 \\
Completa & 762.138 & 1.252,3 & 427,0 & 7,76 & 0,76 \\
\bottomrule
\end{tabular}
\end{table}

A média agregada esconde a interação algoritmo--política. A Tabela~\ref{tab:viabilidade} reporta, por célula, a taxa de viabilidade e os trechos inviáveis médios. Sob Completa, MP-EAVNS e ALNS atingem 100\,\% de viabilidade (todas as 368 execuções); as construtivas ficam abaixo de 52\,\%. Sob Gradual, ambas as metaheurísticas mantêm-se acima de 98\,\% com apenas 0,01 trecho inviável médio --- a coincidência corresponde às mesmas cinco combinações instância-período, casos estruturalmente apertados para o orçamento de busca adotado. As inviabilidades das construtivas sob Completa são predominantemente algorítmicas: a infraestrutura está toda disponível, mas sequências mal estruturadas produzem arcos que o reparo guloso não corrige.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{8pt}
\renewcommand{\arraystretch}{1.1}
\caption{Viabilidade e trechos inviáveis médios por algoritmo e política. Cada célula agrega 368 execuções.}
\label{tab:viabilidade}
\begin{tabular}{lrrrrrr}
\toprule
Algoritmo & \multicolumn{2}{c}{Depósito} & \multicolumn{2}{c}{Gradual} & \multicolumn{2}{c}{Completa} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(l){6-7}
& Viab. & Inv. & Viab. & Inv. & Viab. & Inv. \\
\midrule
EDD & 7,9 & 16,42 & 27,7 & 3,95 & 28,5 & 3,94 \\
Sweep & 9,2 & 9,55 & 50,3 & 1,65 & 51,9 & 1,63 \\
Nearest & 7,9 & 8,69 & 49,7 & 1,13 & 51,6 & 1,10 \\
GRASP & 14,4 & 7,33 & 89,1 & 0,12 & 92,1 & 0,08 \\
ALNS & 17,9 & 4,45 & 98,6 & 0,01 & \textbf{100,0} & \textbf{0,00} \\
MP-EAVNS & 17,9 & 4,83 & 98,6 & 0,01 & \textbf{100,0} & \textbf{0,00} \\
\bottomrule
\end{tabular}
\end{table}

Restringindo a comparação a soluções com $I(x_t) = 0$ (Tabela~\ref{tab:viavel-distancia}), neutraliza-se o termo $\beta$ e isola-se o desempenho de roteamento puro: a MP-EAVNS produz rotas 6,7\,\% mais curtas que a ALNS sob Completa (1.072 vs.\ 1.149 unidades) e 6,2\,\% sob Gradual.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{8pt}
\renewcommand{\arraystretch}{1.1}
\caption{Distância média entre soluções viáveis, por algoritmo e política.}
\label{tab:viavel-distancia}
\begin{tabular}{lrrr}
\toprule
Algoritmo & Depósito & Gradual & Completa \\
\midrule
EDD & 137,0 & 370,1 & 366,0 \\
Sweep & 165,0 & 975,3 & 953,6 \\
Nearest & 145,7 & 725,9 & 707,6 \\
GRASP & 191,4 & 1.238,6 & 1.185,9 \\
ALNS & 188,9 & 1.158,9 & 1.148,9 \\
MP-EAVNS & 188,4 & 1.087,5 & \textbf{1.072,0} \\
\bottomrule
\end{tabular}
\end{table}

A distância sob Depósito (coluna 1) é menor apenas porque contém os casos geometricamente fáceis (clientes próximos ao depósito); a comparação relevante de distância está entre Gradual e Completa, que cobrem subconjuntos comparáveis de execuções viáveis. O cenário Depósito é dominado por inviabilidade estrutural --- clientes além de $B/2$ não podem ser atendidos sem estações intermediárias --- enquanto em Gradual e Completa a inviabilidade desaparece para as metaheurísticas, e a métrica relevante passa a ser a distância em soluções viáveis.

\subsection{MP-EAVNS versus ALNS}

A ALNS adaptada (Seção~\ref{subsec:algoritmos}) é a referência natural para janelas de tempo. Ambos os métodos partem da melhor entre Nearest, EDD e Sweep com 2-opt; a MP-EAVNS adiciona construções randomizadas do GRASP ao pool de sementes. Como a MP-EAVNS reduz o objetivo médio em 36,0\,\% frente ao próprio GRASP (Tabela~\ref{tab:algoritmos}), o laço VNS concentra a maior parte do ganho e o GRASP atua como diversificação inicial. A comparação usa a mesma contagem de iterações ($K=80$), embora a ALNS custe 14,44\,s contra 3,73\,s da MP-EAVNS --- ou seja, sob orçamento de iterações, não de CPU. Três aspectos:

\begin{itemize}
\item Viabilidade. Empate: 100\,\% sob Completa e 98,6\,\% sob Gradual (Tabela~\ref{tab:viabilidade}).
\item Objetivo agregado. A ALNS apresenta objetivo 7,8\,\% menor (MP-EAVNS 8,4\,\% acima), diferença que vem do regime Depósito --- ALNS tem 4,45 trechos inviáveis médios contra 4,83 da MP-EAVNS, possivelmente pela maior diversidade de seus operadores de destruição.
\item Distância em soluções viáveis. Restringindo a $I(x_t)=0$, a MP-EAVNS é 6,7\,\% melhor que a ALNS sob Completa (1.072 vs.\ 1.149) e 6,2\,\% melhor sob Gradual (Tabela~\ref{tab:viavel-distancia}) --- o regime operacional de interesse.
\end{itemize}

A Tabela~\ref{tab:robustez} resume a comparação pareada sob Completa, em execuções viáveis. A vantagem média da MP-EAVNS é de 76,9 unidades de distância (IC 95\,\%: $[65{,}4,\,88{,}4]$). O ganho não é uniforme: nas instâncias pequenas há empate técnico; nas grandes, a MP-EAVNS vence em 88,8\,\% dos pares.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{7pt}
\renewcommand{\arraystretch}{1.1}
\caption{Comparação pareada MP-EAVNS versus ALNS em soluções viáveis sob Completa.}
\label{tab:robustez}
\begin{tabular}{lrrrr}
\toprule
Classe & Casos & Vitórias MP & Empates & Dif. média \\
\midrule
Pequenas & 144 & 17,4\,\% & 73,6\,\% & 1,5 \\
Grandes & 224 & 88,8\,\% & 0,0\,\% & 125,4 \\
Total & 368 & 60,9\,\% & 28,8\,\% & 76,9 \\
\bottomrule
\end{tabular}
\end{table}

O alto número de empates nas pequenas é esperado: com poucos clientes, ambos os métodos atingem soluções de mesma distância. A ALNS vence em 10,3\,\% dos pares totais (9,0\,\% pequenas, 11,2\,\% grandes), mostrando que a vantagem da MP-EAVNS não é universal --- a diferença principal aparece nas grandes, onde a herança oferece um ponto de partida mais informativo.

\subsection{Variantes Reduzidas da MP-EAVNS}

As três variantes definidas na Seção~\ref{subsec:algoritmos} isolam o papel do 2-opt auxiliar, da perturbação e da herança entre períodos:

\begin{itemize}
\item Remover o 2-opt auxiliar tem efeito pequeno (+0,7\,\% no objetivo, nulo na viabilidade), porque o reparo energético continua ativo na avaliação e $\mathcal{N}_1$ cobre a maior parte das melhorias de 2-opt. O atraso médio menor (0,5 contra 1,7) é residual e reflete apenas uma troca local entre distância, rotas e atraso.
\item Remover a perturbação custa +0,9\,\% no objetivo, sugerindo que ela contribui pouco quando $\mathcal{N}_1$--$\mathcal{N}_5$ já encontrou todas as melhorias acessíveis.
\item Remover a herança entre períodos é o componente mais crítico: o objetivo médio cresce 19,7\,\%, a distância de 1.071 para 1.175 e o atraso de 1,7 para 45,8. A inicialização herdada carrega a maior fração do ganho, sobretudo nos períodos finais.
\end{itemize}

\subsection{Sensibilidade à Bateria}

Sob a política Gradual, aumentar a autonomia reduz rapidamente a inviabilidade: a MP-EAVNS passa de 0,22 trechos inviáveis médios em $B=60$ para 0,01 em $B=80$ e zero em $B=100$ (Tabela~\ref{tab:bateria}). A distância da Tabela~\ref{tab:bateria} é média sobre todas as execuções da MP-EAVNS em cada nível de bateria; por isso, em $B=80$, difere da Tabela~\ref{tab:viavel-distancia}, que condiciona a média às soluções viáveis. Depois dessa transição, a inviabilidade energética deixa de ser o gargalo principal.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{8pt}
\renewcommand{\arraystretch}{1.1}
\caption{Sensibilidade da MP-EAVNS à autonomia sob a política Gradual.}
\label{tab:bateria}
\begin{tabular}{rrrrrr}
\toprule
$B$ & Viabilidade & Inviáveis médios & Distância & Atraso & Recargas \\
\midrule
60 & 82,6\,\% & 0,22 & 1.143,7 & 8,9 & 12,26 \\
80 & 98,6\,\% & 0,01 & 1.075,6 & 1,7 & 6,09 \\
100 & 100,0\,\% & 0,00 & 1.054,4 & 0,0 & 1,74 \\
\bottomrule
\end{tabular}
\end{table}

A análise foi executada apenas para a MP-EAVNS; comparar a robustez da ALNS em $B=60$ exigiria uma rodada adicional de experimentos.

\subsection{Custo Computacional}

A Figura~\ref{fig:runtime} cruza tempo de execução e qualidade. A MP-EAVNS custa em média 3,73\,s por solução, contra 0,35\,s do GRASP e 14,44\,s da ALNS: cerca de 10,8 vezes mais lenta que o GRASP (mas com objetivo 36,0\,\% menor) e 3,9 vezes mais rápida que a ALNS, ainda produzindo rotas mais curtas em soluções viáveis (Tabela~\ref{tab:viavel-distancia}). As construtivas puras custam frações de milissegundo, ao preço da viabilidade (Tabela~\ref{tab:viabilidade}).

\begin{figure}[ht]
\centering
\includegraphics[width=0.68\textwidth]{figures/drone_routing_review/runtime_tradeoff.pdf}
\caption{Tempo médio por solução versus objetivo médio nos principais algoritmos.}
\label{fig:runtime}
\end{figure}

\section{Conclusão} \label{sec:conclusao}

Este artigo apresentou o PRMD-ER, uma extensão multi-período do E-VRPTW para roteamento de drones com estações disponibilizadas gradualmente. A MP-EAVNS foi avaliada nas 92 instâncias do \textit{benchmark} E-VRPTW (9.936 execuções totais), contra heurísticas construtivas, GRASP, ALNS adaptada e três variantes reduzidas. A MP-EAVNS reduziu o objetivo penalizado em 36,0\,\% frente ao GRASP, atingiu 100\,\% de viabilidade sob a política Completa e produziu rotas 6,7\,\% mais curtas que a ALNS nesse regime; o estudo confirma que a herança entre períodos é o componente que mais contribui para o ganho.

O resultado central é que a disponibilização gradual preserva 98,6\,\% da viabilidade da política Completa e apresenta distância viável apenas 1,4\,\% superior à desse regime --- a operação não precisa esperar pela infraestrutura total para se aproximar do melhor desempenho observado. Trabalhos futuros podem incorporar modelos energéticos mais realistas e tratar a disponibilização de estações como variável de decisão do planejamento.

\bibliographystyle{sbc}
\bibliography{refs}

\end{document}
