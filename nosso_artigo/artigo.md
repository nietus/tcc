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

\title{Roteamento Multi-Período de Drones com Janelas de Tempo e Estações de Recarga}

\author{Antonio S. C. Neto\inst{1}, Zenilton K. G. do Patrocínio\inst{1}}

\address{Pontifícia Universidade Católica de Minas Gerais (PUC Minas)
\email{\{antonio.couto, zenilton\}@pucminas.br}
}

\begin{document}

\maketitle

\begin{abstract}
This paper studies a multi-period extension of the E-VRPTW problem for drone delivery under phased availability of recharging stations. Demand and external charging stations are activated gradually, and routes are evaluated by distance, tardiness and energy-infeasibility penalties. The proposed MP-EAVNS is an energy-aware Variable Neighborhood Search that combines local search, energy repair and warm starts from previous periods. In 9{,}936 runs over 92 instances, MP-EAVNS reaches 100\,\% viable solutions under full station availability and 98.6\,\% under phased availability. Under full availability, it produces viable routes 6.7\,\% shorter than an adapted ALNS and 9.6\,\% shorter than GRASP; under phased availability, its viable-route distance is only 1.4\,\% above full availability. The results suggest that gradual station activation can preserve most of the routing benefit of full availability.
\end{abstract}

\begin{resumo}
Este artigo estuda uma extensão multi-período do problema E-VRPTW para entregas por drones com disponibilização gradual de estações de recarga. A demanda e as estações externas tornam-se disponíveis progressivamente, e as rotas são avaliadas por distância, atraso e penalidades de inviabilidade energética. A MP-EAVNS proposta é uma Busca em Vizinhança Variável sensível à energia que combina busca local, reparo energético e inicialização herdada entre períodos. Em 9.936 execuções sobre 92 instâncias, a MP-EAVNS atinge 100\,\% de soluções viáveis sob disponibilidade completa de estações e 98,6\,\% sob disponibilidade faseada. Na política completa, produz rotas viáveis 6,7\,\% mais curtas que uma ALNS adaptada e 9,6\,\% mais curtas que o GRASP; na política faseada, sua distância viável fica apenas 1,4\,\% acima da disponibilidade completa. Os resultados indicam que a disponibilização gradual da infraestrutura pode preservar boa parte do benefício da disponibilidade total.
\end{resumo}

\section{Introdução} \label{sec:introducao}

Problemas de roteamento formam uma das bases da otimização combinatória aplicada à logística. O Problema de Roteamento de Veículos (\textit{Vehicle Routing Problem}, VRP) \cite{dantzig1959truck} generaliza a decisão de construir rotas para uma frota, enquanto variantes com janelas de tempo, como o VRPTW \cite{solomon1987algorithms}, incorporam compromissos entre custo espacial e nível de serviço. Outras extensões, como coleta-entrega \cite{savelsbergh1995general,li2001metaheuristic} e roteamento dinâmico \cite{psaraftis1988dynamic,berbeglia2010dynamic,pillac2013review}, mostram que restrições temporais, decisões sequenciais e operadores de reparo são componentes recorrentes em problemas logísticos reais.

A eletrificação da frota acrescenta uma restrição adicional: a rota só é operacionalmente viável se respeitar a autonomia do veículo e a disponibilidade de recarga. O E-VRPTW \cite{schneider2014evrptw} tornou-se uma referência para esse cenário ao combinar janelas de tempo, bateria limitada e estações intermediárias; seu conjunto de instâncias \cite{goeke2019evrptwdata} deriva das instâncias de Solomon e é amplamente usado para comparação experimental. Revisões recentes de roteamento verde e veículos elétricos reforçam que infraestrutura de recarga, autonomia e escolha de estações não são apenas detalhes operacionais, mas decisões que afetam diretamente a estrutura das rotas \cite{asghari2021green,ghorbani2020environmentally,stamadianos2023routing}.

Em drones de entrega, essa dependência é ainda mais forte. A autonomia é menor, a capacidade de carga é reduzida e a margem energética tende a ser mais apertada do que em veículos terrestres. Revisões sobre sistemas de entrega por drones destacam autonomia, recarga e pontos de apoio como fatores centrais de planejamento \cite{raivi2023drone}. Trabalhos recentes já estudam veículos aéreos não tripulados (\textit{Unmanned Aerial Vehicles}, UAVs) com janelas de tempo e recarga via ALNS \cite{shi2023uav}, formulações multiobjetivo para roteamento verde de UAVs \cite{coelho2017green}, localização-roteamento com estações em aplicações industriais \cite{ribeiro2020uav} e roteamento de drones com localização de estações em armazéns \cite{vichitkunakorn2024stocktaking}.

Apesar desses avanços, a maior parte da literatura considera um único horizonte de decisão e assume que a infraestrutura de recarga está fixa e disponível desde o início. Essa hipótese é forte para operações em expansão: uma rede de entregas por drones tende a crescer gradualmente, tanto pela entrada de novos clientes quanto pela disponibilização progressiva de estações externas. Nesse contexto, uma decisão relevante não é apenas qual rota construir com a infraestrutura completa, mas quanto desempenho pode ser preservado antes que toda a infraestrutura esteja disponível.

Este artigo investiga essa questão por meio do PRMD-ER, uma extensão multi-período \textit{offline} do E-VRPTW reinterpretada para drones. Em cada período, há um conjunto de clientes ativos $C_t$ e um conjunto de estações externas disponíveis $F_t$; ambos crescem ao longo do horizonte. Três políticas de estações são comparadas: apenas depósito, disponibilidade faseada e disponibilidade completa. As janelas de tempo e a bateria são tratadas como restrições flexíveis, com penalidades explícitas para atraso e inviabilidade energética.

Para resolver o problema, é proposta a MP-EAVNS, uma Busca em Vizinhança Variável sensível à energia. O método combina construção randomizada, cinco vizinhanças de clientes, reparo energético por visitas a estações existentes e inicialização herdada entre períodos. A escolha por uma família VNS/ALNS é coerente com a literatura de roteamento com múltiplas restrições, na qual operadores de vizinhança, destruição-reconstrução e reparo são amplamente usados para lidar com soluções parcialmente inviáveis \cite{ropke2006adaptive,mladenovic1997variable,cai2022variable,zhou2024memetic}.

A contribuição do trabalho é tripla: formalizar um cenário multi-período de entregas por drones com disponibilização gradual de estações, avaliar o impacto dessa disponibilização sobre a viabilidade energética e comparar a MP-EAVNS com heurísticas construtivas, GRASP e uma ALNS adaptada. Os resultados separam objetivo penalizado, viabilidade energética e distância em soluções viáveis, de modo que o efeito da infraestrutura possa ser analisado sem confundir penalidade por inviabilidade com qualidade de roteamento.

O restante do artigo está organizado da seguinte forma. A Seção~\ref{sec:relacionados} posiciona o PRMD-ER frente à literatura de roteamento com janelas de tempo, metaheurísticas, roteamento verde e drones com recarga. A Seção~\ref{sec:metodologia} formaliza o problema, descreve as políticas de disponibilidade de estações e detalha a MP-EAVNS. A Seção~\ref{sec:resultados} apresenta os experimentos, separando viabilidade, qualidade das rotas e custo computacional. Por fim, a Seção~\ref{sec:conclusao} resume os principais achados e limitações.

\section{Trabalhos Relacionados} \label{sec:relacionados}

A literatura relevante para este trabalho organiza-se em quatro frentes: o VRP clássico e suas extensões com coleta-entrega e janelas de tempo; as metaheurísticas para roteamento; o roteamento verde e os veículos elétricos; e o roteamento de drones com recarga.

\subsection{Roteamento com Janelas de Tempo: Antecedentes}

O VRPTW \cite{solomon1987algorithms} introduziu o compromisso entre custo espacial e nível de serviço temporal e é a base direta do E-VRPTW adotado neste trabalho. Linhas paralelas, como coleta-entrega (PDP) \cite{savelsbergh1995general,li2001metaheuristic} e roteamento dinâmico \cite{psaraftis1988dynamic,berbeglia2010dynamic,pillac2013review}, ajudaram a consolidar operadores como realocação, troca, 2-opt, divisão e união de rotas. O PRMD-ER usa esses operadores, mas seu problema-base é E-VRPTW \textit{offline}: não há chegada de pedidos durante o período, e cada período é resolvido sobre o conjunto observado $C_t$.

\subsection{Metaheurísticas para Problemas de Roteamento}

Sob informação parcial e restrições acopladas, métodos exatos perdem tração rapidamente, o que levou a literatura de roteamento a consolidar metaheurísticas baseadas em vizinhanças e reparo. A ALNS \cite{ropke2006adaptive} adapta a escolha de operadores de destruição e reconstrução conforme o desempenho histórico, enquanto a VNS \cite{mladenovic1997variable} alterna vizinhanças distintas para escapar de ótimos locais. Algoritmos meméticos seguem a mesma lógica híbrida: combinam busca populacional com refinamento local especializado, como mostram propostas recentes para PDP com operadores adaptados à precedência \cite{zhou2024memetic}.

A literatura recente de DPDP, sintetizada na revisão de \cite{cai2023survey}, reforça que decisões sequenciais, informação parcial e múltiplas restrições operacionais exigem métodos capazes de corrigir soluções incompletas ou degradadas ao longo da busca. Nesse contexto, aplicações de VNS a variantes práticas do problema \cite{cai2022variable} indicam que alternar vizinhanças estruturais e aplicar operadores de reparo são mecanismos recorrentes em soluções competitivas. O PRMD-ER adota essa linha, mas desloca o foco para viabilidade energética e disponibilização gradual de infraestrutura.

\subsection{Roteamento Verde, Veículos Elétricos e Recarga}

A viabilidade energética, antes ausente do VRP clássico, foi gradualmente incorporada pela literatura de roteamento verde. Revisões do \textit{Green VRP} \cite{asghari2021green} e classificações de variantes ambientalmente amigáveis \cite{ghorbani2020environmentally} cobrem veículos elétricos, recarga e troca de baterias; análises de problemas com veículos elétricos e autônomos \cite{stamadianos2023routing} destacam recarga e infraestrutura como decisões de primeira classe.

Dentro dessa linha, o E-VRPTW \cite{schneider2014evrptw} estabeleceu a referência para roteamento elétrico com janelas de tempo: veículos com bateria limitada atendem clientes e podem visitar estações intermediárias para recarga. O conjunto de instâncias associado \cite{goeke2019evrptwdata} deriva das instâncias de Solomon e inclui clientes, depósito, estações e parâmetros energéticos. O PRMD-ER usa essa base e acrescenta três elementos: períodos com clientes ativos crescentes $C_t$, políticas de disponibilidade de estações $F_t$ e uma avaliação penalizada que separa objetivo, viabilidade energética e distância em soluções viáveis.

\subsection{Roteamento de Drones e Estações de Recarga}

Em drones, a margem energética é tipicamente menor do que em veículos elétricos terrestres, o que faz com que problemas reais raramente sejam apenas geométricos. Revisões de sistemas de entrega por drones \cite{raivi2023drone} organizam a literatura em planejamento de trajetória, recarga e segurança, evidenciando que autonomia, recarga e disponibilidade de pontos de apoio afetam diretamente o roteamento.

Sobre esse pano de fundo, diversos trabalhos atacaram o roteamento de UAVs com recarga em variantes específicas. Há estudos com janelas de tempo e recarga resolvidos via ALNS, com instâncias derivadas de Solomon na ausência de \textit{benchmarks} padronizados \cite{shi2023uav}; formulações multiobjetivo com autonomia limitada e múltiplas estações \cite{coelho2017green}; localização-roteamento de UAVs com estações para inspeção de correias transportadoras na mineração \cite{ribeiro2020uav}, ilustrando a relevância industrial do tema; e combinações de localização de estações com roteamento de drones para inventário em armazéns \cite{vichitkunakorn2024stocktaking}.

Em conjunto, esses trabalhos confirmam a relevância da combinação UAV + recarga + localização, mas tratam, em geral, um horizonte único e uma infraestrutura fixa, conhecida a priori. A possibilidade de que a infraestrutura de recarga evolua ao longo do tempo --- e que decisões de roteamento precisem ser tomadas sob essa evolução --- permanece aberta. É essa lacuna que o presente trabalho aborda. A Tabela~\ref{tab:literatura} resume as cinco referências mais próximas e situa a contribuição.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.2}
\caption{Posicionamento contextual em relação a trabalhos relacionados.}
\label{tab:literatura}
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lp{4.6cm}p{4.0cm}p{4.4cm}@{}}
\toprule
Ref. & Problema e instâncias & Método e resultado & Relação com este artigo \\
\midrule
\cite{schneider2014evrptw} & E-VRPTW com janelas e estações; 36 pequenas e 56 grandes. & VNS/TS; iguala CPLEX nas pequenas; gap de 0,35\,\% nas grandes. & Principal referência de \textit{benchmark} e método. \\
\cite{shi2023uav} & UAV com janelas e recarga; instâncias derivadas de Solomon. & ALNS superior a ACO e VNS. & Confirma a adequação de ALNS/VNS a UAVs com recarga. \\
\cite{coelho2017green} & Roteamento verde multiobjetivo de UAVs com autonomia e estações. & MILP resolvido por matheurística; fronteira de Pareto. & Mostra relevância multiobjetivo no domínio. \\
\cite{ribeiro2020uav} & Localização-roteamento de UAVs para inspeção industrial. & Formulação MILP em cenário de mineração. & Reforça a criticidade da localização de estações. \\
\cite{vichitkunakorn2024stocktaking} & Drones para inventário em armazéns com localização de estações. & ALNS com codificação específica. & Acopla rota e estações em horizonte único. \\
Este artigo & PRMD-ER sobre E-VRPTW adaptado; 92 instâncias, 4 períodos, 3 políticas. & MP-EAVNS multi-período com herança e reparo energético. & Crescimento multi-período e políticas de disponibilidade de estações. \\
\bottomrule
\end{tabular}%
}
\end{table}

\section{Metodologia} \label{sec:metodologia}

Esta seção apresenta a formulação do PRMD-ER, as instâncias utilizadas, os algoritmos comparados e o método principal MP-EAVNS. São descritos a entrada de clientes, a disponibilidade de estações, a construção de rotas, o reparo energético e a herança entre períodos.

\subsection{Formulação do Problema} \label{subsec:formulacao}

Seja $G=(V,A)$ um grafo completo euclidiano com vértices $V = \{0\} \cup C \cup F$, em que $0$ denota um único depósito, $C$ é o conjunto de clientes e $F$ é o conjunto de estações candidatas. A formulação adota um depósito único por instância, em conformidade com o \textit{benchmark} E-VRPTW \cite{schneider2014evrptw,goeke2019evrptwdata} usado nos experimentos; a generalização para múltiplos depósitos é direta no nível conceitual e está apontada como trabalho futuro. Cada cliente $i \in C$ possui demanda $q_i$, tempo de serviço $s_i$ e janela de atendimento $[a_i, b_i]$. Cada arco $(i,j) \in A$ tem distância euclidiana $d_{ij}$, e o tempo de viagem é proporcional a $d_{ij}/v$, em que $v$ é a velocidade constante do drone. A frota é homogênea, com capacidade de carga $Q$ e bateria $B$. A bateria é modelada diretamente em unidades de distância: ao sair do depósito ou de uma estação, o drone parte com $B$ unidades, e cada arco $(i,j)$ percorrido consome $d_{ij}$ unidades de bateria. Assim, $B = 80$ significa que o drone pode voar 80 unidades de distância antes de precisar recarregar. O modelo energético é intencionalmente simples: o consumo depende apenas da distância euclidiana, não da carga transportada, do vento, da altitude ou de fases de pouso e decolagem. Essa simplificação é coerente com o \textit{benchmark} E-VRPTW adotado e preserva a comparabilidade entre algoritmos, mas constitui uma limitação discutida na Seção~\ref{sec:conclusao}.

O horizonte é dividido em períodos $T = \{1, \ldots, H\}$. Em cada período $t$, apenas um subconjunto $C_t \subseteq C$ de clientes está ativo e apenas um subconjunto $F_t \subseteq F$ de estações externas está disponível. Os dois conjuntos só crescem ao longo dos períodos: $C_t \subseteq C_{t+1}$ e $F_t \subseteq F_{t+1}$. O conjunto $C_t$ é determinado por ordenação angular crescente em torno do depósito, a partir do eixo horizontal positivo, simulando uma expansão por setores da área atendida; sua cardinalidade é $|C_t|=\lceil |C| \cdot t/H \rceil$. O depósito permanece disponível como ponto de recarga em todos os cenários; as políticas abaixo controlam apenas a disponibilidade das estações externas:

\begin{itemize}
\item Depósito: $F_t = \emptyset$ em todo período, isto é, não há estações externas disponíveis e a recarga intermediária só pode ocorrer no próprio depósito;
\item Faseada: as estações externas são disponibilizadas em $H$ parcelas, sendo $|F_t| = \lceil |F| \cdot t/H \rceil$ a cardinalidade do conjunto externo disponível no período $t$. As estações concretas escolhidas para entrar em $F_t \setminus F_{t-1}$ são selecionadas por uma regra gulosa que minimiza, a cada estação adicionada, a soma das distâncias dos clientes em $C_t$ à estação disponível mais próxima --- isto é, cada nova estação é disponibilizada onde mais aproxima a infraestrutura dos clientes já atendidos no período. Esse acoplamento entre crescimento de demanda e expansão de infraestrutura é uma característica do PRMD-ER que não aparece em variantes E-VRPTW puras;
\item Completa: $F_t = F$ em todo período, ou seja, toda a infraestrutura está disponível desde $t = 1$.
\end{itemize}

Uma solução do período $t$ é um conjunto de rotas $x_t = \{R_1, \ldots, R_m\}$, em que $m=R(x_t)$, que começam e terminam no depósito, atendem cada cliente em $C_t$ exatamente uma vez, podem conter paradas intermediárias no depósito ou em estações de $F_t$, e respeitam a capacidade de carga: para cada rota $R$, $\sum_{i \in R \cap C} q_i \leq Q$. Denotando por $D(x_t)$ a distância total, $A(x_t)$ o atraso total, $R(x_t)$ o número de rotas e $I(x_t)$ o número de trechos energeticamente inviáveis remanescentes após o reparo, a função objetivo penalizada do período $t$ é:
\begin{equation}
\min \; \mathcal{F}(x_t) \;=\; D(x_t) \;+\; \alpha\, A(x_t) \;+\; \gamma\, R(x_t) \;+\; \beta\, I(x_t)
\label{eq:objetivo}
\end{equation}
com pesos fixados em $\alpha = 10$, $\gamma = 100$ e $\beta = 10^6$. Os valores de $\alpha$ e $\gamma$ são compatíveis com as magnitudes de distância e número de rotas nas instâncias avaliadas. Já $\beta$ é deliberadamente dominante: uma solução com trecho energeticamente inviável não deve dominar soluções viáveis apenas por ter menor distância ou menor atraso.

A função penalizada é usada como escalar único para aceitação de movimentos durante a busca, enquanto a análise final separa seus componentes em objetivo, viabilidade e distância viável. Bateria, janelas de tempo e número de rotas são, portanto, tratados como termos ponderados, não como restrições rígidas. Essa escolha separa dois casos: inviabilidade algorítmica, quando a busca não encontra uma combinação viável apesar da infraestrutura disponível, e inviabilidade estrutural, quando as estações de $F_t$ não bastam para conectar a rota. Como o reparo considera no máximo uma parada intermediária entre dois vértices consecutivos, arcos que exigiriam duas ou mais recargas são classificados como inviáveis. Nos experimentos, esse limite não impede viabilidade sob a política Completa com $B \geq 80$, em que a MP-EAVNS atinge $I(x_t)=0$ em todas as execuções.

Formalmente, o atraso de uma rota é
\begin{equation}
A(R) \;=\; \sum_{i \in R \cap C} \max\!\bigl(0,\; \tau_i(R) - b_i\bigr)
\label{eq:atraso}
\end{equation}
em que $\tau_i(R)$ é o instante de início do serviço em $i$ ao longo de $R$. Denotando por $e(R,i)$ o nível de bateria disponível em $i$ na rota $R$ e por $i^-$ o vértice anterior a $i$ na mesma rota, a invariante de autonomia é
\begin{equation}
\begin{aligned}
e(R, i) \; &=\; e(R, i^-) - d_{i^- i} \;\geq\; 0 \\
e(R, i^-) \; &=\; B \quad \text{se } i^- \in \{0\}\cup F_t
\end{aligned}
\label{eq:autonomia}
\end{equation}
Na segunda linha, $e(R,i^-)=B$ representa a recarga antes da saída de $i^-$ quando o vértice anterior é o depósito ou uma estação ativa.
A contagem de trechos inviáveis após o reparo é
\begin{equation}
I(x_t) \;=\; \sum_{R \in x_t} \bigl| \{ (i, j) \in R \,:\, e(R, j) < 0 \} \bigr|
\label{eq:inviabilidade}
\end{equation}
em que $(i,j)\in R$ denota um par de vértices consecutivos na sequência da rota.

A Figura~\ref{fig:problem} ilustra uma rota avaliada em um período do PRMD-ER. O drone parte do depósito $0$, visita clientes ativos e usa a estação $f$ como parada intermediária de recarga antes de concluir a rota.

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

\subsection{Instâncias e Cenários}

As instâncias são derivadas do \textit{benchmark} E-VRPTW \cite{schneider2014evrptw,goeke2019evrptwdata}. Cada arquivo contém depósito, clientes, estações de recarga, demandas, janelas de tempo e tempos de serviço. Para o cenário de drones, as distâncias são tratadas de forma euclidiana, a autonomia $B$ é controlada experimentalmente e a energia consumida é proporcional à distância percorrida.

Cada instância é expandida em $H = 4$ períodos. Os clientes são ativados progressivamente pela ordenação angular definida na Seção~\ref{subsec:formulacao}, simulando uma expansão por setores da área atendida. Os experimentos utilizam todas as 92 instâncias disponíveis: 36 instâncias pequenas, com 5, 10 e 15 clientes, e 56 instâncias grandes, com 100 clientes. Os experimentos principais fixam $B = 80$ unidades de distância e os experimentos de sensibilidade variam $B \in \{60, 80, 100\}$.

\subsection{Algoritmos Comparados} \label{subsec:algoritmos}

Foram implementados nove algoritmos: três heurísticas construtivas, um método de construção randomizada com melhoria local, uma metaheurística adaptativa de referência (ALNS), o método principal MP-EAVNS e três variantes reduzidas da MP-EAVNS, cada uma com um componente desativado, para isolar o efeito de cada um:

\begin{itemize}
\item EDD (\textit{Earliest Due Date}): ordena clientes pelo fim da janela $b_i$;
\item Sweep: ordena clientes pelo ângulo polar em relação ao depósito;
\item Nearest: constrói rotas escolhendo, a cada passo, o cliente viável mais próximo;
\item GRASP: construção randomizada por lista restrita seguida de melhoria 2-opt;
\item ALNS: \textit{Adaptive Large Neighborhood Search} \cite{ropke2006adaptive} inicializada pela melhor solução entre Nearest, EDD e Sweep com refinamento 2-opt, com três operadores de destruição (remoção aleatória, remoção do pior, remoção por relação espacial), dois operadores de reparo (inserção gulosa e \textit{regret-2}, que prioriza clientes cuja segunda melhor inserção é muito pior que a melhor), aceitação por \textit{simulated annealing} \cite{kirkpatrick1983optimization} e pesos de operadores atualizados pelo esquema $\sigma$ de Ropke e Pisinger \cite{ropke2006adaptive};
\item MP-EAVNS: método principal, descrito na Seção~\ref{subsec:mpeavns};
\item MP-EAVNS (sem herança): variante que substitui a herança multi-período por uma construção Nearest a frio em cada período;
\item MP-EAVNS (sem perturbação): variante que encerra a busca assim que nenhuma vizinhança encontra melhoria, sem aplicar perturbação aleatória;
\item MP-EAVNS (sem 2-opt auxiliar): variante que omite as chamadas extras de 2-opt antes do laço principal e após perturbações; o reparo energético durante a avaliação permanece ativo.
\end{itemize}

Após qualquer construção, um módulo de reparo energético percorre cada rota da esquerda para a direita simulando o nível de bateria $e(R, \cdot)$ conforme a Equação~\eqref{eq:autonomia}. Sempre que um arco $(i, j)$ faria a bateria atingir um valor negativo --- isto é, quando violaria a condição $e(R,j)\geq 0$ ---, o módulo procura uma estação já ativa $f \in F_t$ para usar como parada intermediária entre $i$ e $j$, segundo dois critérios cumulativos:
\begin{enumerate}
\item Viabilidade: $f$ deve ser alcançável a partir de $i$ com a bateria corrente, isto é, $e(R, i) \geq d_{if}$, e o arco seguinte $f \to j$ deve ser viável após a recarga em $f$, isto é, $B \geq d_{fj}$;
\item Custo mínimo: entre todas as estações que satisfazem a viabilidade, é escolhida aquela que minimiza o aumento de distância $\Delta_{ij}(f) = d_{if} + d_{fj} - d_{ij}$.
\end{enumerate}
Se nenhuma estação em $F_t$ satisfizer simultaneamente os dois critérios, o arco permanece inviável e contribui com uma unidade em $I(x_t)$. Após a parada intermediária (ou após a contabilização da violação), o módulo continua a simulação a partir do próximo vértice da rota; a bateria, se houve recarga em $f$, é reiniciada em $B$. O módulo modela a decisão operacional de desviar para a base de recarga geometricamente mais próxima cujo voo de ida ainda cabe na bateria corrente e cujo voo de saída até o próximo cliente cabe em uma bateria cheia.

O trajeto passa por $i \to f \to j$; não há retorno a $i$ depois da recarga. Também não há criação \textit{ad hoc} de estações: o conjunto $F$ é fixo pela instância e $F_t$ é determinado pela política, de modo que o reparo apenas escolhe qual das estações já instaladas será visitada. Essa separação entre o roteamento (sequência de clientes) e o reparo energético (escolha da estação) reduz o espaço de busca e torna os algoritmos comparáveis: todos os métodos da Seção~\ref{subsec:algoritmos} produzem apenas a sequência de clientes; o módulo de reparo é o mesmo em todos os casos.

O reparo é guloso por arco: ele minimiza o aumento local de distância em $(i,j)$, mas não otimiza conjuntamente todo o conjunto de paradas de recarga da rota. Essa escolha reduz o custo de avaliação e mantém a comparação entre algoritmos uniforme, mas pode deixar de encontrar a melhor sequência global de estações.

\subsection{MP-EAVNS} \label{subsec:mpeavns}

A MP-EAVNS estende a VNS clássica \cite{mladenovic1997variable} para o ambiente multi-período com reparo energético. O método parte da melhor solução inicial entre EDD, Sweep, Nearest e múltiplas execuções da construção randomizada do GRASP, e em seguida explora cinco vizinhanças encadeadas de clientes. Seja $\mathcal{N}_k(x_t)$ a vizinhança $k$ da solução corrente $x_t$, para $k=1,\ldots,5$, e seja $x_t' \in \mathcal{N}_k(x_t)$ uma solução candidata. A busca aceita apenas movimentos que reduzem a função objetivo:
\begin{equation}
x_t \leftarrow x_t' \qquad \text{se} \quad \mathcal{F}(x_t') < \mathcal{F}(x_t)
\label{eq:aceitacao}
\end{equation}

As vizinhanças de clientes e o reparo energético usado na avaliação são:

\begin{itemize}
\item $\mathcal{N}_1$ -- 2-opt intra-rota: inverte um trecho de uma rota para reduzir distância;
\item $\mathcal{N}_2$ -- realocação: remove um cliente e o reinsere na melhor posição (intra- ou inter-rota);
\item $\mathcal{N}_3$ -- troca: troca dois clientes entre posições (intra- ou inter-rota);
\item $\mathcal{N}_4$ -- divisão: separa em duas uma rota cuja distância acumulada excede a autonomia;
\item $\mathcal{N}_5$ -- união: combina duas rotas curtas quando há folga de bateria e capacidade;
\item $\mathcal{R}_E$ -- reparo energético: durante a avaliação, contabiliza uma parada em uma estação já ativa $f \in F_t$ sempre que o arco $(i,j)$ violar a autonomia, escolhendo a parada que produz o menor aumento de distância $d_{if} + d_{fj} - d_{ij}$.
\end{itemize}

A Figura~\ref{fig:neighborhoods} ilustra cada movimento sobre uma rota pequena, mostrando o estado antes e depois da operação. Em todos os painéis, a linha superior representa o estado anterior e a linha inferior representa o estado posterior; quadrados denotam o depósito, círculos denotam clientes, triângulos denotam estações de recarga e as arestas em destaque (laranja) marcam os arcos modificados.

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

\subsection{Herança Multi-Período} \label{subsec:multiperiodo}

A lógica multi-período não altera a busca local; ela altera o ponto de partida. Dada a melhor solução $x_t^\star$ do período $t$, o período $t+1$ começa com essa solução e insere os novos clientes $C_{t+1} \setminus C_t$ nas rotas de menor aumento marginal. Em seguida, a MP-EAVNS executa a busca normalmente. Essa inicialização herdada representa operações em expansão, nas quais parte das rotas tende a permanecer estável entre ciclos.

\section{Resultados} \label{sec:resultados}

Os experimentos utilizam todas as 92 instâncias do \textit{benchmark} E-VRPTW reinterpretado (36 pequenas, com 5--15 clientes, e 56 grandes, com 100 clientes), quatro períodos, três políticas de estações e nove algoritmos, totalizando $92 \times 4 \times 3 \times 9 = 9.936$ execuções, todas com bateria fixa em $B = 80$ unidades de distância. Os experimentos foram executados em um processador Intel Core i7-13650HX (16 GB de RAM), em Windows 11, usando Python 3.12.10 e uma única \textit{thread} por execução. As subseções a seguir analisam, em ordem, o desempenho por algoritmo, a interação entre algoritmo e política, a comparação cabeça-a-cabeça entre MP-EAVNS e ALNS, as variantes reduzidas da MP-EAVNS, a sensibilidade à bateria e o custo computacional.

\subsection{Comparação entre Algoritmos}

A Tabela~\ref{tab:algoritmos} apresenta as métricas médias agregadas sobre as três políticas. O objetivo penalizado segue a Equação~\eqref{eq:objetivo} e, como $\beta = 10^6$, é fortemente dominado pelo número de trechos energeticamente inviáveis. Por esse motivo, a análise também inclui a taxa de viabilidade (fração de execuções com $I(x_t) = 0$) e, nas tabelas subsequentes, métricas restritas a soluções viáveis, que isolam o desempenho de roteamento puro do efeito da penalidade.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.1}
\caption{Métricas médias por algoritmo nas 1.104 execuções de cada método (todas as políticas, $B=80$).}
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
MP-EAVNS (principal) & 1.617.556 & 1.071,0 & 1,7 & 14,31 & 1,62 \\
\quad variante sem 2-opt aux. & 1.630.227 & 1.071,9 & 0,5 & 14,32 & 1,63 \\
\quad variante sem perturb. & 1.632.965 & 1.076,4 & 1,6 & 14,38 & 1,63 \\
\quad variante sem herança & 1.936.032 & 1.174,6 & 45,8 & 14,29 & 1,93 \\
\bottomrule
\end{tabular}
\vspace{1mm}
{\footnotesize Rotas indica o número médio de rotas $R(x_t)$ por solução; o número médio de recargas é reportado separadamente na Tabela~\ref{tab:estacoes}.\par}
\end{table}

Em termos relativos, considerando o objetivo penalizado, a MP-EAVNS reduz o objetivo médio em 36,0\,\% frente ao GRASP e 56--80\,\% frente às heurísticas construtivas, e fica 8,4\,\% acima da ALNS. A ALNS, por sua vez, reduz o objetivo em 40,9\,\% frente ao GRASP. Essa leitura agregada, porém, é afetada pela política Depósito, que representa um limite inferior sem estações externas e produz muitas inviabilidades estruturais. Por isso, a Figura~\ref{fig:algorithm-summary} separa a viabilidade por política e compara a distância apenas nos regimes com infraestrutura externa. Em Faseada e Completa, ALNS e MP-EAVNS praticamente empatam em viabilidade, mas a MP-EAVNS produz rotas viáveis mais curtas.

\begin{figure}[ht]
\centering
\includegraphics[width=0.82\textwidth]{figures/drone_routing_review/algorithm_summary.pdf}
\caption{Viabilidade por política (a) e distância média entre soluções viáveis nas políticas Faseada e Completa (b), considerando GRASP, ALNS e MP-EAVNS.}
\label{fig:algorithm-summary}
\end{figure}

Quando a agregação é restrita às políticas com infraestrutura externa (Faseada e Completa), a diferença no objetivo penalizado entre ALNS e MP-EAVNS praticamente desaparece: 9.374 contra 9.306, respectivamente (diferença de 0,7\,\%). Assim, a vantagem agregada da ALNS na Tabela~\ref{tab:algoritmos} deve ser lida como efeito do regime Depósito, não como superioridade geral de roteamento nos cenários operacionais de interesse.

\subsection{Efeito da Política de Estações}

A Tabela~\ref{tab:estacoes} compara as três políticas de estações agregando todos os algoritmos. A coluna Recargas indica o número médio de visitas a pontos de recarga, distinto do número de rotas penalizado na Equação~\eqref{eq:objetivo}. A política Completa funciona como limite superior de infraestrutura, pois todas as estações externas estão disponíveis desde o primeiro período. A política Faseada, por sua vez, representa a disponibilização gradual: ela fica apenas 2,3\,\% acima da Completa no objetivo penalizado e 89,5\,\% abaixo da política Depósito, indicando que a disponibilização progressiva recupera quase todo o benefício energético da infraestrutura completa. As distâncias médias de Faseada e Completa são praticamente iguais (1.253,9 contra 1.252,3, diferença de 0,1\,\%); a degradação da Faseada aparece mais no atraso (431,9 contra 427,0, diferença de 1,1\,\%) e na pequena inviabilidade residual.

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
Faseada & 779.701 & 1.253,9 & 431,9 & 7,73 & 0,77 \\
Completa & 762.138 & 1.252,3 & 427,0 & 7,76 & 0,76 \\
\bottomrule
\end{tabular}
\end{table}

A média agregada esconde uma interação relevante entre algoritmo e política. A Tabela~\ref{tab:viabilidade} reporta, por célula, a taxa de viabilidade e o número médio de trechos inviáveis. Sob a política Completa, tanto a MP-EAVNS quanto a ALNS atingem 100\,\% de viabilidade --- todas as 368 execuções produzem rotas energeticamente viáveis ---, enquanto as construtivas ficam abaixo de 52\,\%. Sob a política Faseada, ambas as metaheurísticas mantêm-se acima de 98\,\% de viabilidade, com apenas 0,01 trecho inviável médio, e o GRASP atinge 92,1\,\%. A coincidência entre ALNS e MP-EAVNS na política Faseada corresponde às mesmas cinco combinações instância-período, sugerindo casos estruturalmente apertados para o orçamento de busca adotado. Sob Completa, a quase totalidade das inviabilidades remanescentes das construtivas é algorítmica (Seção~\ref{subsec:formulacao}): a infraestrutura está toda disponível, mas sequências de clientes mal estruturadas ainda podem produzir arcos que o reparo guloso por arco não consegue corrigir.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{8pt}
\renewcommand{\arraystretch}{1.1}
\caption{Viabilidade e trechos inviáveis médios por algoritmo e política. Cada célula agrega 368 execuções.}
\label{tab:viabilidade}
\begin{tabular}{lrrrrrr}
\toprule
Algoritmo & \multicolumn{2}{c}{Depósito} & \multicolumn{2}{c}{Faseada} & \multicolumn{2}{c}{Completa} \\
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

Por outro lado, restringindo a comparação a soluções viáveis, a Tabela~\ref{tab:viavel-distancia} reporta a distância média entre soluções viáveis, isto é, calculada apenas sobre execuções com $I(x_t) = 0$. Essa visão neutraliza o termo de penalidade $\beta$ e isola o desempenho de roteamento puro. A MP-EAVNS produz rotas mais curtas que a ALNS por 6,7\,\% sob Completa (1.072 contra 1.149 unidades) e por 6,2\,\% sob Faseada.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{8pt}
\renewcommand{\arraystretch}{1.1}
\caption{Distância média entre soluções viáveis, por algoritmo e política.}
\label{tab:viavel-distancia}
\begin{tabular}{lrrr}
\toprule
Algoritmo & Depósito & Faseada & Completa \\
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

A distância média entre soluções viáveis sob Depósito (coluna 1 da Tabela~\ref{tab:viavel-distancia}) é menor que sob as outras políticas porque essa coluna contém apenas os casos geometricamente fáceis, nos quais os clientes estão próximos o suficiente do depósito. A comparação relevante de distância é, portanto, entre Faseada e Completa, que cobrem subconjuntos comparáveis de execuções viáveis.

Lendo em conjunto as Tabelas~\ref{tab:viabilidade} e~\ref{tab:viavel-distancia}, a comparação por política não deve ser lida isoladamente. O cenário Depósito é dominado por inviabilidade estrutural: clientes distantes mais de $B/2$ do depósito não podem ser atendidos sem estações intermediárias. Já em Faseada e Completa, ALNS e MP-EAVNS praticamente eliminam a inviabilidade; nesse regime, a métrica mais informativa passa a ser a distância das soluções viáveis.

\subsection{MP-EAVNS versus ALNS}

A ALNS adaptada ao PRMD-ER (Seção~\ref{subsec:algoritmos}) é uma referência natural para problemas de roteamento com janelas de tempo. Sua solução inicial é a melhor entre Nearest, EDD e Sweep com refinamento 2-opt; a MP-EAVNS usa a mesma base construtiva e acrescenta múltiplas construções randomizadas do GRASP ao conjunto de sementes. Essa assimetria favorece a MP-EAVNS no ponto de partida, portanto a comparação não atribui o ganho apenas ao laço VNS. Como a MP-EAVNS reduz o objetivo médio em 36,0\,\% frente ao próprio GRASP (Tabela~\ref{tab:algoritmos}), o laço VNS concentra a maior parte do ganho, e a inclusão do GRASP atua como diversificação do ponto de partida.

A comparação usa a mesma contagem de iterações principais ($K=80$), mas não o mesmo tempo de relógio: a ALNS custa em média 14,44\,s por solução, contra 3,73\,s da MP-EAVNS. Portanto, os resultados abaixo comparam estratégias sob orçamento de iterações, não sob orçamento de CPU. Uma calibração por tempo poderia alterar a fronteira custo--qualidade da ALNS e fica fora do escopo experimental. A comparação cabeça-a-cabeça apresenta três aspectos:

\begin{itemize}
\item Viabilidade. ALNS e MP-EAVNS empatam, ambas com 100\,\% de viabilidade sob Completa e 98,6\,\% sob Faseada (Tabela~\ref{tab:viabilidade}). Para a viabilidade energética isoladamente, os dois métodos são equivalentes.
\item Objetivo agregado. A ALNS apresenta objetivo médio 7,8\,\% menor que a MP-EAVNS na agregação sobre as três políticas; de forma equivalente, a MP-EAVNS fica 8,4\,\% acima da ALNS. A diferença vem essencialmente do regime Depósito, em que a ALNS apresenta um número ligeiramente menor de trechos inviáveis estruturais (4,45 contra 4,83 médios), possivelmente associado à maior diversidade de seus operadores de destruição.
\item Distância entre soluções viáveis. Restringindo a comparação a execuções com $I(x_t) = 0$, a MP-EAVNS é 6,7\,\% melhor que a ALNS sob Completa (1.072 contra 1.149 unidades de distância; Tabela~\ref{tab:viavel-distancia}) e 6,2\,\% melhor sob Faseada. Esse é o regime operacional de interesse, em que a infraestrutura permite viabilidade total e a métrica relevante é o custo de roteamento.
\end{itemize}

Em síntese, ALNS e MP-EAVNS apresentam a mesma garantia empírica de viabilidade sob infraestrutura suficiente. A diferença está no comportamento posterior à viabilidade: quando as estações permitem rotas factíveis, a MP-EAVNS explora melhor a estrutura multi-período e produz rotas mais curtas; quando a infraestrutura é escassa, a ALNS reduz ligeiramente o número de trechos inviáveis.

\paragraph{Robustez por classe de instância.} A Tabela~\ref{tab:robustez} resume a comparação pareada entre MP-EAVNS e ALNS sob a política Completa, considerando apenas execuções viáveis. A vantagem média da MP-EAVNS é de 76,9 unidades de distância, com intervalo de confiança de 95\,\% igual a $[65{,}4,\,88{,}4]$. Um teste pareado de Wilcoxon, com hipótese alternativa de menor distância para a MP-EAVNS, indica vantagem estatisticamente significativa ($p < 10^{-33}$). O ganho, porém, não é uniforme: nas instâncias pequenas os métodos praticamente empatam; nas grandes, a MP-EAVNS vence em 88,8\,\% dos pares.

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

O alto número de empates nas instâncias pequenas é esperado: com poucos clientes, ambos os métodos alcançam soluções de mesma distância em grande parte dos casos. A ALNS produz rotas mais curtas em 10,3\,\% dos pares totais, distribuídos em ambas as classes (9,0\,\% nas pequenas e 11,2\,\% nas grandes), mostrando que a vantagem da MP-EAVNS não é universal. A diferença principal aparece nas instâncias grandes, em que o espaço de busca cresce e a herança multi-período passa a oferecer um ponto de partida mais informativo.

\subsection{Variantes Reduzidas da MP-EAVNS}

As três variantes reduzidas definidas na Seção~\ref{subsec:algoritmos} isolam o papel do 2-opt auxiliar, da perturbação e da herança entre períodos. A interpretação dos resultados é a seguinte:

\begin{itemize}
\item Remover o 2-opt auxiliar tem efeito pequeno sobre o objetivo (+0,7\,\%) e nulo sobre a viabilidade, porque o reparo energético continua ativo durante a avaliação e o movimento $\mathcal{N}_1$ já cobre a maior parte das melhorias de 2-opt durante a busca principal. O atraso médio dessa variante é menor (0,5 contra 1,7), mas ambos os valores são residuais frente ao objetivo agregado; a diferença indica apenas uma troca local entre distância, rotas e atraso, não uma melhora global da variante.
\item Remover a perturbação também tem efeito pequeno (+0,9\,\% no objetivo), sugerindo que a perturbação aleatória contribui pouco para os ganhos finais quando a busca local em $\mathcal{N}_1$--$\mathcal{N}_5$ já encontrou todas as melhorias possíveis.
\item Remover a herança entre períodos é o componente que mais impacta o desempenho: o objetivo médio cresce 19,7\,\%, a distância média sobe de 1.071 para 1.175 unidades e o atraso médio sobe de 1,7 para 45,8 unidades. Isso confirma que a inicialização herdada carrega a maior fração do ganho, em particular nos períodos finais, quando rotas estáveis reduzem o esforço para inserir novos clientes.
\end{itemize}

Em conjunto, as variantes reduzidas indicam que a herança entre períodos é o componente que mais distingue a MP-EAVNS de uma VNS estática aplicada período a período; os demais componentes do laço de busca contribuem ganhos pequenos mas consistentes.

\subsection{Sensibilidade à Bateria}

Sob a política Faseada, aumentar a autonomia do drone reduz rapidamente a penalidade por inviabilidade. A Tabela~\ref{tab:bateria} mostra essa transição: com $B=60$, a MP-EAVNS ainda mantém em média 0,22 trechos inviáveis por execução; com $B=80$, esse valor cai para 0,01; com $B=100$, a inviabilidade desaparece nas 368 execuções. Depois dessa transição, a inviabilidade energética deixa de ser o gargalo principal.

\begin{table}[ht]
\centering
\small
\setlength{\tabcolsep}{8pt}
\renewcommand{\arraystretch}{1.1}
\caption{Sensibilidade da MP-EAVNS à autonomia sob a política Faseada. Recargas indica o número médio de visitas a estações de recarga por solução.}
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

Essa análise de sensibilidade foi executada apenas para a MP-EAVNS. Portanto, ela identifica o limiar de autonomia em que o método proposto deixa de ser limitado por bateria, mas não permite concluir se a ALNS seria mais robusta que a MP-EAVNS em $B=60$. Essa comparação exige uma rodada adicional de experimentos com os mesmos níveis de autonomia para a ALNS.

\subsection{Custo Computacional}

A Figura~\ref{fig:runtime} cruza tempo de execução e qualidade da solução. A MP-EAVNS custa em média 3,73\,s por solução, contra 0,35\,s do GRASP e 14,44\,s da ALNS. Ela ocupa, portanto, um ponto intermediário do compromisso custo--qualidade: é cerca de 10,8 vezes mais lenta que o GRASP, mas reduz o objetivo em 36,0\,\%; é 3,9 vezes mais rápida que a ALNS e produz rotas mais curtas em soluções viáveis (Tabela~\ref{tab:viavel-distancia}). As construtivas puras custam frações de milissegundo, mas pagam o preço em viabilidade (Tabela~\ref{tab:viabilidade}). Para o cenário-alvo deste trabalho, em que rotas são replanejadas por período, o tempo da MP-EAVNS permanece na escala de segundos.

\begin{figure}[ht]
\centering
\includegraphics[width=0.68\textwidth]{figures/drone_routing_review/runtime_tradeoff.pdf}
\caption{Tempo médio por solução versus objetivo médio nos principais algoritmos.}
\label{fig:runtime}
\end{figure}

\section{Conclusão} \label{sec:conclusao}

Este artigo apresentou o PRMD-ER, uma extensão multi-período do problema E-VRPTW para roteamento de drones com estações de recarga disponibilizadas gradualmente. A MP-EAVNS foi avaliada em uma base experimental formada pelas 92 instâncias do \textit{benchmark} E-VRPTW, totalizando 9.936 execuções com heurísticas construtivas, GRASP, uma ALNS adaptada e três variantes reduzidas do próprio método. A MP-EAVNS reduziu o objetivo penalizado médio em 36,0\,\% frente ao GRASP, atingiu 100\,\% de viabilidade sob a política Completa e produziu rotas viáveis 6,7\,\% mais curtas que a ALNS nesse regime de viabilidade total. A variante sem herança teve o maior impacto negativo, o que confirma a importância de usar a solução do período anterior como ponto de partida.

O resultado central é que a disponibilização gradual de estações preserva 98,6\,\% da viabilidade obtida com disponibilidade completa e fica a apenas 1,4\,\% de distância da política Completa em soluções viáveis. Isso indica que a operação não precisa esperar pela disponibilidade total da infraestrutura para se aproximar do regime de melhor desempenho.

As principais limitações estão no modelo físico adotado para os drones. O consumo energético foi tratado como proporcional apenas à distância euclidiana, sem considerar carga transportada, vento, altitude, velocidade, fases de pouso e decolagem ou degradação da bateria. Essa simplificação preserva a comparabilidade com o \textit{benchmark} E-VRPTW, mas limita a leitura operacional dos resultados. Trabalhos futuros podem incorporar modelos energéticos mais realistas, estimar tempos de recarga dependentes da bateria e tratar a disponibilização de estações como variável de decisão do planejamento.

\bibliographystyle{sbc}
\bibliography{refs}

\end{document}
