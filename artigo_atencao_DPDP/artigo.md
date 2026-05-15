
\documentclass[a4paper,11pt]{article}
\usepackage{sbpo-template}
%\usepackage[latin1]{inputenc}
\usepackage[brazil]{babel} % português do Brasil
\usepackage[utf8]{inputenc} % acentos no UTF-8
\usepackage[T1]{fontenc} % para hifenização correta
\usepackage{amsmath,amssymb}
\usepackage{url}
\usepackage[square]{natbib}
\usepackage{indentfirst}
\usepackage{fancyhdr}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,fit,calc,shapes.geometric,backgrounds}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\includegraphics[scale=0.5]{sbpo2026-header-logo.png}}
%\renewcommand{\headrulewidth}{0pt}
\renewcommand{\headruleskip}{-1mm}
%\setlength\headheight{101.0pt}
%\addtolength{\textheight}{-101.0pt}
\setlength\headheight{86pt}
\addtolength{\textheight}{-86pt}
\setlength{\headsep}{5mm}
\setlength{\footskip}{4.08003pt}

\begin{document}

\title{Uma Abordagem Baseada em Atenção para o Problema de Coletas e Entregas Dinâmicas}

% Batch-Enforced Assignment for Smart Transportation
\maketitle
\thispagestyle{fancy}

%\author{
%\name{Antonio S. Neto, Rodrigo D. Macedo, Sandro J Almeida}
%\institute{Deeptera Sistemas Inteligentes}
%iaddress{Departamento de Pesquisa \& Desenvolvimento}
%\email{ \{antonio,rodrigo,sandro\}@deeptera.com}
%}

\vspace{8mm}
\begin{resumo}
O Problema de Coletas e Entregas Dinâmicas (\textit{Dynamic Pickup and Delivery Problem} - DPDP) busca criar planos de despacho para uma frota de veículos diante de pedidos revelados dinamicamente, sem conhecimento prévio completo. Além da incerteza temporal, o problema envolve restrições operacionais como capacidade dos veículos, precedência entre coleta e entrega, regras de descarregamento e atrasos acumulados, o que dificulta o uso direto de métodos exatos em cenários de decisão contínua. Este trabalho propõe uma abordagem baseada em Modelo de Atenção treinado via Aprendizado por Reforço e combinado com busca local. O modelo foi adaptado ao DPDP por meio de atributos temporais e operacionais, máscaras de viabilidade e refinamento local das rotas geradas. A avaliação no benchmark ICAPS 2021 indica que a abordagem proposta reduz o custo médio agregado em 98,7\% comparado à regra Round-Robin e em 16,3\% em relação à Busca Tabu, além de superar o algoritmo genético em 31,2\% nos grupos 1--56.

\end{resumo}

\bigskip
\begin{palchaves}
Problema de Coletas e Entregas Dinâmicas, Modelo de Atenção, Aprendizado por Reforço, Roteamento de Veículos, Inteligência Artificial.
\end{palchaves}

\vspace{8mm}

\begin{abstract}
The \textit{Dynamic Pickup and Delivery Problem} (DPDP) requires dispatch plans for a fleet of vehicles under dynamically revealed requests and incomplete prior information. Beyond temporal uncertainty, the problem includes operational constraints such as vehicle capacity, pickup-and-delivery precedence, unloading order and accumulated delays, which make exact methods difficult to apply in continuous decision settings. This work proposes an Attention Model trained with Reinforcement Learning and combined with local search. The model is adapted to the DPDP through temporal and operational features, feasibility masks and local route refinement. Experiments on the ICAPS 2021 benchmark indicate that the proposed approach reduces aggregate average cost by 98.7\% compared to the Round-Robin rule and by 16.3\% relative to Tabu Search, while outperforming the genetic algorithm by 31.2\% average reduction in groups 1--56.

\end{abstract}

\bigskip
\begin{keywords}
Dynamic Pickup and Delivery Problem, Attention Model, Reinforcement Learning, Vehicle Routing, Artificial Intelligence.
\end{keywords}

\bigskip
\section{Introdução}

O problema de otimização de rotas é um dos temas centrais da pesquisa em otimização
combinatória e logística computacional. Em sua forma mais elementar, o
\textit{Travelling Salesman Problem} (TSP) \citep{applegate2006traveling} consiste em
determinar o caminho de menor custo que visita um conjunto de nós exatamente uma vez
e retorna à origem --- um problema NP-difícil cuja complexidade cresce com o número de cidades. O TSP serve como caso base para uma vasta família de problemas
de roteamento com aplicações diretas em manufatura, telecomunicações e distribuição
logística.

A incorporação de uma frota de veículos com capacidade finita origina o
\textit{Vehicle Routing Problem} (VRP) \citep{dantzig1959truck}, no qual o objetivo
é minimizar o custo total de rotas que coletivamente atendam a um conjunto de
clientes com demandas conhecidas. Extensões canônicas do VRP introduzem restrições
de janelas de tempo (\textit{VRPTW}) \citep{solomon1987algorithms}, frotas
heterogêneas (\textit{HFVRP}), múltiplos depósitos (\textit{MDVRP}) e combinações
dessas variantes, cada qual modelando aspectos distintos de cenários reais de
distribuição urbana e industrial.

Uma subclasse relevante do VRP é o \textit{Pickup and Delivery Problem} (PDP)
\citep{savelsbergh1995general}, que generaliza o problema ao exigir que cada requisição
seja composta por um par de nós --- um ponto de coleta (\textit{pickup}) e um ponto
de entrega (\textit{delivery}) --- com a restrição de precedência de que a coleta
deve ocorrer antes da entrega correspondente. O PDP captura cenários de transporte de
cargas entre origens e destinos distintos, como operações de redistribuição de
contêineres e serviços de compartilhamento de veículos. Variantes como o
\textit{PDPTW} \citep{li2001metaheuristic} acrescentam janelas de tempo estritas a cada nó, e variantes como o
\textit{PDPLIFO} \citep{cordeau2010branch} impõem restrições de ordem de carregamento do tipo
\textit{Last-In-First-Out} (LIFO) aos veículos.

No escopo do gerenciamento de cadeias de suprimentos de manufatura em larga escala e operações de logística urbana, o \textit{Dynamic Pickup and Delivery Problem} (DPDP) emerge como um desafio de otimização combinatória NP-difícil \citep{garey1979computers, cai2023survey} que é uma variação do Pickup and Delivery Problem (PDP). O DPDP requer o despacho e o roteamento contínuo de uma frota de veículos para atender a requisições de transporte de cargas entre nós de coleta e entrega, cujas informações (distribuição espacial, janelas de tempo, volume de carga) são reveladas de forma estocástica e contínua ao longo do horizonte temporal \citep{psaraftis1988dynamic, hao2022introduction, liu2017dynamic}.

Instâncias práticas do DPDP são encontradas em diversos setores. Na logística de \textit{e-commerce} e \textit{last-mile delivery}, plataformas de entrega urbana precisam rotear continuamente seus veículos à medida que novos pedidos chegam ao longo do dia \citep{ulmer2017restaurant}. Em cadeias de suprimentos industriais, fábricas com múltiplos centros de distribuição geram requisições de transporte de paletes entre plantas com janelas de tempo estritas \citep{su2021heterogeneous}. Serviços de \textit{ride-sharing} e transporte sob demanda, como táxis compartilhados, enfrentam versões do DPDP onde passageiros solicitam viagens com origens e destinos distintos em tempo real \citep{bouros2011dynamic}. Plataformas colaborativas de logística, incluindo modelos de \textit{crowdshipping}, também introduzem variantes do DPDP com tempos de viagem dependentes do horário \citep{stoia2023dynamic}. Em todos esses cenários, a natureza dinâmica das requisições e a necessidade de decisões em tempo real tornam o problema particularmente desafiador.

Historicamente, o DPDP foi abordado sob a ótica de reotimizações periódicas valendo-se de programação matemática inteira mista ou metaheurísticas de busca local \citep{karami2020periodic, ropke2005adaptive}. Contudo, o aumento da escala do problema torna a convergência de métodos exatos intratável, ao passo que métodos heurísticos sofrem de ineficiência computacional ou miopia na generalização sobre espaços de estados não estacionários.

Este trabalho propõe uma solução utilizando um Modelo de Atenção \citep{kool2019attention}. O objetivo é apresentar a arquitetura de atenção para o problema do DPDP e fazer uma comparação analítica com outros métodos.

O texto está dividido da seguinte forma: A Seção 2 apresenta uma revisão da literatura, traçando a evolução dos algoritmos de DPDP e usos recentes de Modelos de Atenção em problemas de logística e transporte. A Seção 3 detalha a modelagem do Modelo de Atenção adaptado ao DPDP, explicitando os processos de projeção de \textit{embeddings}, extração de contexto global via \textit{Encoder} e decodificação com mascaramento físico contínuo. Na Seção 4, conduzimos comparações dos resultados obtidos com outros algoritmos. Por fim, a Seção 5 sintetiza as conclusões desta pesquisa.

\section{Trabalhos Relacionados}

\cite{karami2020periodic} utilizam uma abordagem de reotimizações usando MILP (Mixed Integer Linear Programming) para resolver o problema do DPDP com janelas de tempo, mas não demonstram nenhuma aplicação em ambientes de escala industrial. Devido à natureza NP-difícil do problema, o tempo computacional exigido por métodos exatos torna-os inviáveis para aplicações operacionais. A literatura consolidou o uso de heurísticas e metaheurísticas como a abordagem mais eficiente, e evoluiu consideravelmente a partir delas. A Busca Adaptativa em Grandes Vizinhanças (ALNS) \citep{ropke2005adaptive} e suas variantes hibridizadas como IALNS-SA \citep{ma2025ialnssa} estabeleceram-se como métodos robustos. Mais recentemente, algoritmos meméticos (método genético com etapas de refinamento locais) \citep{zhou2024memetic} e métodos baseados em Busca em Vizinhança Variável (VNS) \citep{cai2022variable} também foram propostos.

A aplicação de técnicas de Aprendizado por Reforço (RL) e redes neurais ao roteamento de veículos tem ganhado relevância crescente. \cite{li2021learning} propuseram um \textit{framework} baseado em RL para otimizar instâncias do DPDP em escala industrial, demonstrando que políticas aprendidas podem generalizar para cenários não vistos durante o treinamento. \cite{cordeiro2023deep} apresentaram uma abordagem baseada em Aprendizado por Reforço Profundo (DRL) para o despacho dinâmico de veículos, utilizando uma formulação orientada a eventos que permite ao agente tomar decisões de roteamento em tempo real. \cite{jiang2025machine} integraram DRL com teoria de filas para otimizar o roteamento dinâmico de última milha. No contexto de entregas com múltiplas transferências, \cite{chen2021deepfreight} propuseram o DeepFreight, que combina aprendizado por reforço multi-agente (QMIX) com um otimizador MILP para despacho de frotas. Essas abordagens compartilham a vantagem de substituir regras heurísticas fixas por políticas adaptativas, que aprendem padrões latentes nos dados operacionais.

Paralelamente à evolução das metaheurísticas na pesquisa operacional, os Modelos de Atenção emergiram como uma mudança de paradigma nas arquiteturas de redes neurais profundas \citep{attention-survey}. Originalmente concebidos para solucionar gargalos no Processamento de Linguagem Natural (NLP), como no trabalho de \cite{bahdanau2014neural}, os mecanismos de atenção ganharam destaque por sua capacidade de focar seletivamente nos elementos mais relevantes de uma sequência de dados de entrada. Esse avanço permitiu superar limitações de modelos recorrentes tradicionais, especialmente na modelagem de dependências de longo alcance.

Com a introdução da arquitetura Transformer por \cite{vaswani2017attention}, os mecanismos de atenção passaram a ocupar papel central no processamento sequencial, eliminando completamente a necessidade de recorrência e permitindo maior paralelização e eficiência computacional. A partir desse marco, modelos baseados em atenção, como o BERT \citep{devlin2018bert}, consolidaram-se como estado da arte em diversas tarefas de NLP. Posteriormente, a mesma arquitetura Transformer passou a sustentar os \textit{Large Language Models} (LLMs), nos quais o mecanismo de atenção é escalado para grandes volumes de dados e parâmetros.

Além disso, a literatura recente evidencia que os mecanismos de atenção têm sido amplamente aplicados em diferentes domínios além do NLP. Em visão computacional, por exemplo, o Vision Transformer \citep{dosovitskiy2020vit} e o DETR \citep{carion2020detr} demonstram a eficácia da atenção na modelagem de dependências espaciais e na reformulação de problemas clássicos como classificação e detecção de objetos. De forma mais abrangente, estudos de revisão, como \cite{guo2022attentioncv}, destacam o uso de mecanismos de atenção em tarefas como segmentação de imagens, reconhecimento de ações, séries temporais, bioinformática e aprendizado multimodal.

O trabalho de \cite{kool2019attention} demonstrou que um Modelo de Atenção bidirecional, treinado via Aprendizado por Reforço, pode atuar como um poderoso \textit{Encoder-Decoder} para resolver variações estáticas do VRP. A arquitetura utiliza um \textit{Encoder} Transformer para gerar \textit{embeddings} dos nós do grafo e um \textit{Decoder} autorregressivo que constrói a solução nó a nó, empregando atenção com mascaramento para garantir viabilidade. O treinamento é realizado com o algoritmo REINFORCE e uma \textit{baseline} de \textit{greedy rollout}. Os resultados reportados demonstraram desempenho competitivo com heurísticas especializadas no TSP e no CVRP, com tempos de inferência significativamente menores e capacidade de generalização para instâncias de tamanhos variados.

Este trabalho se insere e expande essa linha de pesquisa ao adaptar a arquitetura de atenção especificamente aos desafios estocásticos do DPDP. Enquanto o modelo original de Kool et al. opera sobre instâncias estáticas com todos os nós conhecidos \textit{a priori}, a adaptação proposta lida com requisições reveladas dinamicamente, incorporando informações temporais (prazos, janelas de tempo) e restrições operacionais (capacidade, LIFO, filas de doca) ao vetor de \textit{features} dos nós. Além disso, o modelo é combinado com uma etapa de busca local VNS para refinar as soluções geradas pela atenção, resultando em uma abordagem híbrida que une a capacidade de generalização das redes neurais com a precisão da otimização local.

\section{Metodologia}

Esta seção descreve como o problema foi representado e como a política proposta transforma o estado dinâmico do sistema em decisões de despacho. A metodologia combina três componentes principais: a formulação operacional do DPDP, a representação neural de pedidos e veículos por meio de \textit{embeddings}, e a construção de soluções por um Modelo de Atenção refinado por busca local. Com isso, preserva-se a estrutura logística do problema enquanto o modelo aprende relações entre demanda, capacidade, localização e urgência.

\subsection{Formulação do problema}

O problema é formulado considerando um cenário de despacho contínuo onde existe um conjunto de fábricas $F$, uma frota de veículos $V$ e um conjunto de pedidos $O$ que surgem dinamicamente ao longo do tempo. Cada pedido $o \in O$ é definido por uma fábrica de coleta $p_o$, uma fábrica de entrega $d_o$, uma demanda de carga $q_o$, um instante de revelação (ou criação) $r_o$ e um prazo limite para entrega $l_o$.

O problema é dinâmico porque nem todos os pedidos são conhecidos no início. O simulador avança em ciclos de 10 minutos. Em cada ciclo, o algoritmo recebe os pedidos disponíveis, a posição atual dos veículos e as rotas já comprometidas. A decisão do algoritmo é escolher quais pedidos serão atendidos, por quais veículos e em qual ordem.

A solução construída em um ciclo de despacho é denotada por $S$. A função de custo combina distância total e atraso:
\begin{equation} C(S) = \sum_{v \in V} D_v(S) + \delta \sum_{o \in O} \max(0,\; a_o(S) - l_o) \end{equation}
onde $D_v(S)$ é a distância percorrida pelo veículo $v$, $a_o(S)$ é o instante de entrega do pedido $o$, $l_o$ é seu prazo e $\delta = 10000/3600$. Assim, atrasos recebem uma penalidade alta, enquanto soluções sem atraso são avaliadas principalmente pela distância.

Duas restrições operacionais são consideradas de forma explícita. A primeira é a capacidade: a carga carregada por um veículo não pode exceder sua capacidade. A segunda é a regra LIFO (\textit{Last-In-First-Out}), em que o último item carregado deve ser o primeiro descarregado quando a organização física da carga exige essa ordem \citep{cordeau2010branch}.

\subsection{Representação da entrada}

Antes de aplicar o modelo de atenção, os pedidos são agrupados em blocos. Um bloco é a unidade de decisão usada pelo algoritmo: ele reúne um ou mais itens que compartilham a mesma fábrica de coleta e a mesma fábrica de entrega. Essa escolha reduz o número de decisões individuais e evita que itens naturalmente relacionados sejam tratados como pedidos independentes. Cada bloco é descrito por um vetor de atributos, chamado \textit{embedding} de entrada. Nesse contexto, \textit{embedding} significa apenas uma representação numérica do objeto que será processada pela rede neural.

Cada bloco $b$ é representado por um vetor com informações sobre distância, demanda, prazo e localização:
\begin{equation} \mathbf{x}_b = [\tilde{d}_{p},\; \tilde{d}_{d},\; \tilde{q},\; \tilde{t}_{l},\; \text{lat}_{p},\; \text{lng}_{p},\; \text{lat}_{d},\; \text{lng}_{d}] \end{equation}
onde $\tilde{d}_{p}$ e $\tilde{d}_{d}$ são distâncias normalizadas até a coleta e a entrega, $\tilde{q}$ é a demanda normalizada, $\tilde{t}_{l}$ é o tempo restante até o prazo, e as demais entradas são as coordenadas das fábricas de coleta e entrega.

Cada veículo também é representado por um vetor:
\begin{equation} \mathbf{x}_v = [\text{lat}_v,\; \text{lng}_v,\; \tilde{c}_v,\; \tilde{t}_v,\; \tilde{q}_v] \end{equation}
onde $\tilde{c}_v$ é a capacidade restante, $\tilde{t}_v$ é o tempo estimado até o veículo ficar disponível e $\tilde{q}_v$ é a carga atual. Todos os valores contínuos são normalizados para manter as escalas comparáveis durante a inferência.

A Figura~\ref{fig:metodologia-integrada} resume essa relação entre estado dinâmico, representação, política de atenção, treinamento e refinamento local. As setas contínuas indicam o fluxo de inferência no ciclo de despacho, enquanto as setas tracejadas indicam treinamento ou realimentação para o próximo ciclo.

\begin{figure}[ht]
\centering
\resizebox{0.88\textwidth}{!}{
\begin{tikzpicture}[
font=\scriptsize,
card/.style={draw, rounded corners=3pt, align=center, minimum width=2.7cm, minimum height=0.9cm, inner sep=4pt},
hub/.style={draw, rounded corners=6pt, align=center, minimum width=3.1cm, minimum height=1.2cm, inner sep=5pt, fill=cyan!10},
arrow/.style={-{Latex[length=2.0mm]}, thick},
softarrow/.style={-{Latex[length=2.0mm]}, thick, dashed},
group/.style={draw, rounded corners=4pt, inner sep=6pt}
]

\node[hub] (policy) at (0,0) {Política $\pi_{\theta}$\\\textit{Encoder} + \textit{Decoder}\\pontua ações $(b,v,i)$};

\node[card, fill=orange!12] (state) at (-3.8,1.25) {Estado $s_t$\\pedidos, veículos\\rotas comprometidas};
\node[card, fill=green!10] (repr) at (-3.8,-1.05) {Representação\\blocos $x_b$\\veículos $x_v$};
\node[card, fill=red!8] (mask) at (3.8,1.25) {Máscara\\capacidade\\precedência e LIFO};
\node[card, fill=purple!10] (vns) at (3.8,-1.05) {Refinamento\\VNS iterada\\$S_{\text{best}}$};

\node[card, fill=yellow!18, minimum width=2.55cm] (imit) at (-1.55,-2.65) {Imitação\\\textit{cheapest insertion}};
\node[card, fill=yellow!18, minimum width=2.55cm] (reinforce) at (1.55,-2.65) {REINFORCE\\$R(S)=-C(VNS(S))$};

\draw[arrow] (state) -- (repr);
\draw[arrow] (repr) -- (policy);
\draw[arrow] (policy) -- (mask);
\draw[arrow] (mask) -- (vns);
\coordinate (statefeed) at ([yshift=0.55cm]state.north);
\draw[softarrow] (vns.east) -- ++(0.55,0) |- node[pos=0.77, above, font=\tiny] {rotas atualizadas} (statefeed) -- (state.north);
\draw[softarrow] (imit) -- (policy);
\draw[softarrow] (reinforce) -- (policy);

\node[group, fit=(imit)(reinforce), label=below:{Treinamento da política}] {};
\end{tikzpicture}
}
\caption{Visão integrada da metodologia.}
\label{fig:metodologia-integrada}
\end{figure}

\subsection{Arquitetura do Modelo de Atenção}

O modelo segue a estrutura \textit{Encoder-Decoder} usada em Transformers \citep{vaswani2017attention} e em modelos de atenção para roteamento \citep{kool2019attention}. O \textit{Encoder} lê todos os blocos e veículos disponíveis no ciclo de despacho e produz representações contextualizadas, isto é, vetores que levam em conta não apenas o objeto isolado, mas também sua relação com os demais. O \textit{Decoder} usa essas representações para escolher ações de inserção.

Primeiro, os vetores de blocos e veículos são projetados para uma dimensão comum $d_{\text{model}} = 128$:
\begin{equation} \mathbf{h}_i^{(0)} = W_x \mathbf{x}_i + b_x \end{equation}
onde $i$ indexa um bloco ou veículo, $\mathbf{x}_i$ representa o vetor de entrada desse elemento, $\mathbf{h}_i^{(0)}$ é sua representação oculta inicial, e $W_x$ e $b_x$ são os pesos e o viés aprendidos nessa projeção linear. Em seguida, um \textit{Encoder} Transformer com 3 camadas transforma esses vetores em \textit{embeddings} contextualizados.

O mecanismo básico de atenção é:
\begin{equation} \text{Attn}(Q,K,V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V \end{equation}
onde $Q$ representa a consulta, isto é, o elemento que busca informação; $K$ representa as chaves, usadas para medir a relevância dos demais elementos; e $V$ representa os valores, que carregam a informação agregada após o cálculo dos pesos de atenção. Uma cabeça de atenção é uma comparação independente entre esses três elementos. No modelo multi-cabeça, esse cálculo é repetido em paralelo por 8 cabeças, permitindo que o modelo observe relações diferentes ao mesmo tempo, como urgência, proximidade e capacidade.

\subsection{Treinamento da política}

% Uso de dados sinteticos

O treinamento é feito em duas etapas. Primeiro, o modelo aprende por imitação a reproduzir decisões de uma heurística de inserção mais barata (\textit{cheapest insertion}) \citep{solomon1987algorithms}, que escolhe a posição que causa o menor aumento imediato de custo. Essa etapa fornece uma política inicial estável e evita que o treinamento comece a partir de decisões aleatórias. Seja $\pi_{\theta}$ a política do modelo, parametrizada por $\theta$, que atribui probabilidade às ações possíveis. Em cada passo de decisão $t$, o estado observado é $s_t$ e a ação escolhida pela heurística é $a_t^\star$. A perda de imitação é:
\begin{equation} \mathcal{L}_{IL}(\theta) = -\sum_{t} \log \pi_{\theta}(a_t^\star \mid s_t) \end{equation}
onde $\mathcal{L}_{IL}$ é a perda de aprendizado por imitação. Minimizar essa perda aumenta a probabilidade das ações escolhidas pela heurística nos estados correspondentes.

Para evitar que a política seja ajustada diretamente às instâncias usadas na avaliação final, o treinamento utiliza instâncias sintéticas geradas no mesmo formato do benchmark, com variações no número de pedidos, veículos, fábricas e padrão temporal de chegada dos pedidos. Foram criadas 56 instâncias para treino e 8 instâncias para teste.

Depois, a política é refinada com REINFORCE \citep{williams1992simple}, um método clássico de gradiente de política em Aprendizado por Reforço \citep{sutton2018reinforcement}. Durante esse refinamento, a solução gerada pela política passa pela VNS antes da avaliação. Assim, a recompensa usada é o negativo do custo da solução após o refinamento local:
\begin{equation} R(S) = -C(\text{VNS}(S)) \end{equation}
onde $\text{VNS}(S)$ representa a solução obtida após aplicar a busca local sobre a solução inicial $S$ construída pela política. A atualização da política segue:
\begin{equation} \nabla_{\theta} J(\theta) = \mathbb{E}\left[(R(S)-b)\sum_t \nabla_{\theta}\log \pi_{\theta}(a_t \mid s_t)\right] \end{equation}
onde $J(\theta)$ é o objetivo esperado da política, $a_t$ é a ação amostrada pelo modelo no passo $t$, $\mathbb{E}[\cdot]$ indica a média esperada sobre as soluções geradas e $b$ é uma \textit{baseline} usada para reduzir a variância do gradiente. Na prática, isso faz com que ações que produzem soluções melhores que a referência se tornem mais prováveis, enquanto ações associadas a soluções piores perdem probabilidade. Como a recompensa considera o custo pós-VNS, o treinamento favorece decisões iniciais que não apenas têm baixo custo imediato, mas também conduzem a regiões do espaço de soluções que a busca local consegue refinar com maior eficiência.

A configuração principal do Modelo de Atenção utilizada nos experimentos é resumida na Tabela~\ref{tab:parametros-modelo}.

\begin{table}[ht]
\centering
\caption{Configuração principal do Modelo de Atenção.}
\label{tab:parametros-modelo}
\begin{tabular}{lc}
\toprule
Parâmetro & Valor \\
\midrule
Dimensão dos \textit{embeddings} & 128 \\
Camadas do \textit{Encoder} & 3 \\
Cabeças de atenção & 8 \\
Épocas de imitação & 200 \\
Épocas de REINFORCE & 50 \\
\bottomrule
\end{tabular}
\end{table}

\subsection{Decodificação e construção da solução}

Durante a inferência, o \textit{Decoder} avalia ações do tipo:
\begin{equation} \alpha = (b,\; v,\; i) \end{equation}
onde $b$ é o bloco a inserir, $v$ é o veículo escolhido e $i$ é a posição de inserção na rota. Para cada ação viável, o modelo calcula uma pontuação $u_{\alpha}$. A ação escolhida é:
\begin{equation} \alpha^\star = \operatorname{arg\,max}_{\alpha \in A_{\text{viável}}} u_{\alpha} \end{equation}
A máscara garante que $A_{\text{viável}}$ contenha apenas inserções que respeitam capacidade, ordem de coleta antes da entrega e restrições LIFO. Na construção inicial, usamos uma pequena busca em feixe (\textit{beam search}) \citep{lowerre1976harpy}, mantendo alternativas parciais promissoras para reduzir decisões míopes sem enumerar todas as rotas.

\subsection{Busca local e VNS iterada}

Depois que o modelo de atenção constrói uma solução inicial, aplicamos uma busca local VNS (\textit{Variable Neighborhood Search}) \citep{mladenovic1997variable}. A ideia da VNS é explorar diferentes tipos de vizinhança da solução atual. Em vez de depender de um único operador de melhoria, a busca alterna entre mudanças simples e mudanças um pouco mais estruturadas, o que ajuda a escapar de soluções localmente boas, mas ainda melhoráveis. Esse tipo de busca já foi aplicado diretamente a variantes práticas do DPDP \citep{cai2022variable}.

Seja $\mathcal{N}_k(S)$ a vizinhança $k$ da solução atual. A busca avalia soluções candidatas $S' \in \mathcal{N}_k(S)$ e aceita apenas movimentos que reduzem a função objetivo:
\begin{equation} S \leftarrow S' \quad \text{se} \quad C(S') < C(S) \end{equation}

As vizinhanças usadas são:

\begin{itemize}
\item $\mathcal{N}_1$ - Realocação de bloco: remove um bloco de sua posição atual e testa sua inserção em outras posições e veículos.
\item $\mathcal{N}_2$ - Troca entre veículos: troca dois blocos pertencentes a veículos distintos, respeitando capacidade e LIFO.
\item $\mathcal{N}_3$ - 2-opt: inverte um trecho da sequência de blocos de um veículo para reduzir distância, seguindo a lógica clássica de melhoria local em roteamento \citep{lin1965computer}.
\item $\mathcal{N}_4$ - Agrupamento por rota: move grupos consecutivos com mesma coleta e entrega, preservando rotas com alta concentração de pedidos semelhantes.
\end{itemize}

A Figura~\ref{fig:vns-vizinhancas} ilustra a VNS. Cada vizinhança tenta melhorar a solução atual; quando há melhoria, a busca reinicia a partir da solução atualizada. Quando não há melhoria, o índice $k$ avança para a próxima vizinhança. Se todas as vizinhanças forem testadas, uma perturbação controlada inicia uma nova rodada enquanto houver tempo restante.

\begin{figure}[ht]
\centering
\resizebox{0.78\textwidth}{!}{
\begin{tikzpicture}[
font=\scriptsize,
vnsbox/.style={draw, rounded corners=4pt, align=center, minimum width=3.45cm, minimum height=0.75cm, inner sep=4pt},
decision/.style={draw, diamond, aspect=2.2, align=center, minimum width=2.35cm, minimum height=1.0cm, fill=yellow!18, inner sep=1pt},
terminal/.style={draw, rounded corners=6pt, align=center, minimum width=3.45cm, minimum height=0.75cm, inner sep=4pt, fill=purple!10},
arrow/.style={-{Latex[length=1.8mm]}, thick},
softarrow/.style={-{Latex[length=1.8mm]}, thick, dashed}
]

\node[vnsbox, fill=blue!8] (start) at (0,0) {Solução inicial $S_0$};
\node[vnsbox, fill=green!10] (init) at (0,-1.10) {Inicializa $k=1$};
\node[vnsbox, fill=green!10] (search) at (0,-2.20) {Explora $\mathcal{N}_k(S)$\\gera candidato $S'$};
\node[decision] (improve) at (0,-3.55) {$C(S')<C(S)$?};

\node[vnsbox, fill=cyan!10] (accept) at (-3.95,-3.55) {Aceita\\$S \leftarrow S'$};
\node[vnsbox, fill=orange!12] (advance) at (3.95,-3.55) {Avança\\$k \leftarrow k+1$};
\node[decision] (more) at (3.95,-4.95) {$k \le K$?};

\node[vnsbox, fill=orange!12] (shake) at (0,-4.95) {Perturbação\\$S \leftarrow \tilde{S}$};
\node[decision] (time) at (0,-6.25) {há tempo?};
\node[terminal] (best) at (0,-7.50) {Retorna $S_{\text{best}}$};

\draw[arrow] (start.south) -- (init.north);
\draw[arrow] (init.south) -- (search.north);
\draw[arrow] (search.south) -- (improve.north);
\draw[arrow] (improve.west) -- node[above, font=\tiny, pos=0.50] {sim} (accept.east);
\draw[arrow] (improve.east) -- node[above, font=\tiny, pos=0.50] {não} (advance.west);
\draw[arrow] (advance.south) -- (more.north);
\draw[arrow] (more.west) -- node[above, font=\tiny, pos=0.50] {não} (shake.east);
\draw[arrow] (shake.south) -- (time.north);
\draw[arrow] (time.south) -- node[right, font=\tiny, pos=0.45] {não} (best.north);

\draw[softarrow] (accept.north) -- ++(0,1.05) -| node[pos=0.25, above, font=\tiny] {$k=1$} (search.west);
\draw[softarrow] (more.east) -- ++(0.85,0) |- node[pos=0.25, right, font=\tiny] {sim} (search.east);
\draw[softarrow] (time.west) -- ++(-5.00,0) |- node[pos=0.28, left, font=\tiny] {sim} (init.west);
\end{tikzpicture}
}
\caption{Fluxo iterativo da VNS.}
\label{fig:vns-vizinhancas}
\end{figure}

Também usamos uma versão iterada da VNS. Quando nenhuma vizinhança melhora a solução, uma perturbação controlada é aplicada para gerar uma solução próxima $\tilde{S}$. Em seguida, a VNS é executada novamente a partir de $\tilde{S}$. Apenas a melhor solução encontrada é mantida:
\begin{equation}
S_{\text{best}} = \operatorname{arg\,min}_{S \in \mathcal{P}} C(S)
\end{equation}
onde $\mathcal{P}$ é o conjunto de soluções visitadas durante as rodadas de refinamento. Essa etapa usa o tempo computacional restante para explorar alternativas próximas, sem transformar o método em força bruta, pois apenas um subconjunto pequeno de movimentos viáveis é testado.

\section{Resultados}

A avaliação experimental utiliza o benchmark ICAPS 2021 \citep{hao2022introduction}, composto por 64 instâncias que representam diferentes cenários de operação logística. Essas instâncias são organizadas em 8 grupos de 8 instâncias cada, classificados por ordem crescente de complexidade. O que diferencia um grupo do outro é a escala do problema: instâncias nos primeiros grupos possuem poucos veículos e pedidos (cenário de baixa densidade), enquanto os grupos finais (como 57--64) apresentam centenas de veículos e milhares de pedidos revelados ao longo do tempo, exigindo maior eficiência computacional e capacidade de generalização do modelo. Cada instância é dividida em 144 ciclos de 10 minutos (totalizando um dia operacional). Em cada ciclo, novas demandas podem aparecer, e o algoritmo deve produzir uma nova decisão antes do próximo instante de atualização.

Os resultados comparam o Modelo de Atenção proposto com a Busca Tabu, o algoritmo genético e a regra Round-Robin. Para avaliar o desempenho dos algoritmos, considerou-se duas funções objetivo principais que refletem os custos logísticos e operacionais: $f_1$, que representa a distância total percorrida pela frota, e $f_2$, que quantifica o atraso total acumulado no atendimento dos pedidos.

O custo total de uma solução para uma instância $i$ e o custo médio por grupo são definidos por:
\begin{center}
\begin{minipage}{0.46\textwidth}
\begin{equation}
C_i = f_{1,i} + \lambda f_{2,i}
\end{equation}
\end{minipage}
\hfill
\begin{minipage}{0.46\textwidth}
\begin{equation}
\bar{C}_G = \frac{1}{|G|}\sum_{i \in G} C_i
\end{equation}
\end{minipage}
\end{center}
em que $\lambda = 10000/3600$ é o fator de penalização aplicado ao atraso. Dessa forma, o objetivo central dos algoritmos é minimizar $\bar{C}_G$. Os experimentos foram executados em um processador Intel Core i7-13650HX com 15,69 GB de RAM.

\begin{table}[ht]
\centering
\caption{Comparação entre modelos.}
\label{tab:comparacao-algoritmos}
\resizebox{\textwidth}{!}{
\begin{tabular}{lcccccccc}
\hline
& \multicolumn{2}{c}{Atenção} & \multicolumn{2}{c}{Tabu Search} & \multicolumn{2}{c}{Genético} & \multicolumn{2}{c}{Round-Robin} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}
Grupo & $\bar{C}_G$ & Tempo(s) & $\bar{C}_G$ & Tempo(s) & $\bar{C}_G$ & Tempo(s) & $\bar{C}_G$ & Tempo(s) \\
\hline
1--8 & 1.0279e+03 & 144.27 & \textbf{1.0102e+03} & 195.84 & 1.1902e+03 & 168.87 & 8.2200e+04 & 83.88 \\
9--16 & \textbf{8.4412e+04} & 296.29 & 1.9851e+05 & 251.66 & 2.9962e+05 & 202.10 & 3.0523e+06 & 119.31 \\
17--24 & \textbf{9.4222e+02} & 372.85 & 1.0625e+03 & 268.70 & 1.0677e+03 & 205.78 & 1.8709e+06 & 105.06 \\
25--32 & \textbf{1.6910e+04} & 1386.39 & 5.1047e+04 & 316.63 & 8.9995e+04 & 209.60 & 3.4348e+07 & 158.79 \\
33--40 & 1.3019e+04 & 742.28 & 1.3641e+04 & 324.10 & \textbf{1.1541e+04} & 225.98 & 4.3941e+07 & 149.79 \\
41--48 & \textbf{2.6890e+05} & 1008.74 & 3.3283e+05 & 452.14 & 6.4500e+05 & 232.93 & 4.3177e+08 & 305.77 \\
49--56 & \textbf{4.7752e+06} & 1581.47 & 6.1441e+06 & 521.10 & 6.4574e+06 & 269.91 & 9.2273e+08 & 428.01 \\
57--64 & 3.5008e+07 & 1319.68 & 4.1273e+07 & 834.40 & \textbf{3.1055e+07} & 291.36 & 1.8643e+09 & 767.46 \\
\hline
Média 1--56 & \textbf{7.3720e+05} & 790.33 & 9.6317e+05 & 332.88 & 1.0723e+06 & 216.45 & 2.0540e+08 & 192.94 \\
Média 1--64 & 5.0210e+06 & 856.50 & 6.0019e+06 & 395.57 & \textbf{4.8201e+06} & 225.82 & 4.1276e+08 & 264.76 \\
\hline
\end{tabular}
}

\end{table}

A regra Round-Robin é utilizada como uma política sequencial sem otimização explícita, incapaz de antecipar efeitos futuros de capacidade, prazos e posicionamento da frota. Como esperado, a abordagem proposta supera essa regra em todos os grupos avaliados, indicando que a incorporação de representação neural, máscaras de viabilidade e refinamento local produz ganhos em relação a uma política puramente reativa.

Em relação ao algoritmo genético, o Modelo de Atenção obtém custo médio 31,2\% menor nos grupos 1--56, vencendo em seis dos sete grupos considerados. Esse resultado sugere que a política aprendida gera boas soluções iniciais para a busca local na maioria das escalas. A principal limitação ocorre no grupo 57--64, em que o algoritmo genético apresenta melhor desempenho. Essa queda pode ser atribuída ao aumento do número de veículos, pedidos e ações viáveis, que amplia o espaço de decisão do \textit{Decoder}; à menor capacidade de generalização da política em cenários de escala extrema, devido ao número limitado de instâncias sintéticas utilizadas no treinamento; e às limitações do espaço de vizinhança explorado pela VNS.

A comparação com a Busca Tabu reforça o mesmo padrão. O Modelo de Atenção apresenta menor custo em sete dos oito grupos, com redução média de 16,3\% no custo global 1--64. Apenas no grupo 1--8 a Busca Tabu obtém menor custo. Nos demais grupos, incluindo o de maior escala (57--64), o Modelo de Atenção supera a Busca Tabu.

O Modelo de Atenção apresenta o maior tempo médio agregado entre os métodos comparados, sendo cerca de 2,17 vezes mais lento que a Busca Tabu e 3,79 vezes mais lento que o algoritmo genético. Entretanto, o tempo médio por ciclo é de apenas 5,95 s, equivalente a 0,99\% da janela disponível de 600 s. Portanto, embora o método demande mais processamento agregado, ele permanece compatível com o replanejamento dinâmico exigido pelo DPDP.

\section{Conclusões}

Este trabalho apresentou uma abordagem híbrida para o DPDP baseada em Modelo de Atenção, Aprendizado por Reforço e busca local. A proposta foi motivada pela dificuldade de tomar decisões de despacho em ambientes dinâmicos, nos quais pedidos surgem ao longo do tempo e as rotas precisam respeitar restrições físicas e operacionais. Para lidar com esse cenário, o modelo incorporou atributos temporais, máscaras de viabilidade e uma etapa de refinamento local, buscando combinar generalização aprendida com melhoria heurística das soluções.

Os resultados obtidos no benchmark ICAPS 2021 indicam que a abordagem proposta reduz o custo médio em 98,7\% em relação ao Round-Robin e em 16,3\% em relação à Busca Tabu na média global 1--64. Em comparação com o algoritmo genético, o Modelo de Atenção apresenta custo médio 31,2\% menor nos grupos 1--56, vencendo em seis dos sete grupos considerados nessa média. Entretanto, no grupo 57--64, o algoritmo genético obtém melhor desempenho, fazendo com que a média global 1--64 da abordagem proposta fique 4,17\% acima da média do genético. Esse resultado indica que a política neural é competitiva na maioria das escalas avaliadas, mas ainda depende de mecanismos de refinamento mais robustos para instâncias de maior porte.

Como contribuição principal, este trabalho mostra que uma política baseada em atenção pode ser aplicada a um problema dinâmico de coleta e entrega, no qual as decisões são tomadas repetidamente sob informação parcial e com pedidos revelados ao longo do tempo. A formulação proposta combina representação neural das relações entre pedidos e veículos, máscaras de viabilidade operacional e refinamento local das rotas, oferecendo uma alternativa aprendida para orientar o despacho em cenários dinâmicos.

Como trabalhos futuros, pretende-se ampliar o treinamento com instâncias sintéticas mais diversas e investigar mecanismos de integração mais fortes entre o modelo de atenção e a busca local. Em particular, os resultados nas instâncias 57--64 indicam que a política neural deve ser combinada com operadores de vizinhança mais expressivos, estratégias de múltiplas partidas ou mecanismos adaptativos de seleção de vizinhanças para preservar qualidade em grande escala.

~\\
\bibliographystyle{sbpo}
\bibliography{exemplo-latex}

\end{document}
