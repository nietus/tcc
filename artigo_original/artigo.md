\documentclass[12pt]{article}

\usepackage{sbc-template}
\usepackage{graphicx,url}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}

\sloppy

\title{Abordagem híbrida e adaptativa para o Dynamic Pickup and Delivery Problem}

\author{Antonio S. C. Neto\inst{1}, Zenilton K. G. do Patrocínio\inst{1}}

\address{Pontifícia Universidade Católica de Minas Gerais (PUCMG)
\email{\{antonio.couto, zenilton\}@pucminas.br}
}

\begin{document}

\maketitle

\begin{abstract}
The Dynamic Pickup and Delivery Problem (DPDP) is a dynamic logistics problem frequently encountered in large companies such as Huawei, Amazon, and Uber. The objective of the DPDP is to create an optimized dispatch plan for a fleet of available vehicles, with demands that arise in a stochastic manner. This paper proposes [METHOD PLACEHOLDER] to produce high-quality dispatch decisions under strict time constraints. Experiments on the ICAPS 2021 benchmark demonstrate that [RESULTS PLACEHOLDER].
\end{abstract}

\begin{resumo}
O \textit{Dynamic Pickup and Delivery Problem} (DPDP) é um problema dinâmico de logística encontrado com frequência dentro de grandes empresas como \textit{Huawei, Amazon e Uber}. O objetivo do DPDP é criar um plano de despacho otimizado para uma frota de veículos disponíveis, com demandas que surgem de maneira estocástica. Este artigo propõe [MÉTODO PLACEHOLDER] para produzir decisões de despacho de alta qualidade sob restrições rigorosas de tempo. Experimentos no benchmark ICAPS 2021 demonstram que [RESULTADOS PLACEHOLDER].
\end{resumo}

\section{Introdução}

O problema de otimização de rotas é um dos temas centrais da pesquisa em otimização combinatória e logística computacional. Em sua forma mais elementar, o \textit{Travelling Salesman Problem} (TSP) \cite{applegate2006traveling} consiste em determinar o caminho de menor custo que visita um conjunto de nós exatamente uma vez e retorna à origem — um problema NP-difícil cuja complexidade cresce superpolinomialmente com o número de cidades \cite{garey1979computers}. O TSP serve como base para uma ampla família de problemas de roteamento, com aplicações diretas em manufatura, telecomunicações e distribuição logística. Técnicas de busca local como as trocas \textit{k-opt} \cite{lin1965computer} tornaram-se referência para a resolução eficiente dessas instâncias.

A incorporação de uma frota de veículos com capacidade finita origina o \textit{Vehicle Routing Problem} (VRP) \cite{dantzig1959truck}, no qual o objetivo é minimizar o custo total das rotas que atendem a um conjunto de clientes com demandas conhecidas. Extensões clássicas do VRP incluem restrições de janelas de tempo (VRPTW) \cite{solomon1987algorithms}, frotas heterogêneas \cite{su2021heterogeneous}, múltiplos depósitos e combinações dessas variantes, cada uma modelando diferentes aspectos de cenários reais de distribuição urbana e industrial.

Uma subclasse relevante é o \textit{Pickup and Delivery Problem} (PDP) \cite{savelsbergh1995general}, que generaliza o VRP ao exigir que cada requisição seja composta por um par de nós — um ponto de coleta (\textit{pickup}) e um ponto de entrega (\textit{delivery}) — com a restrição de precedência de que a coleta deve ocorrer antes da entrega correspondente. O PDP modela cenários em que cargas precisam ser transportadas entre origens e destinos distintos, como na redistribuição de contêineres e em serviços de mobilidade compartilhada \cite{bouros2011dynamic}. Variantes como o PDPTW incorporam janelas de tempo estritas, enquanto outras, como o PDPLIFO, impõem restrições operacionais relacionadas à ordem de carregamento e descarregamento dos veículos — em particular, a política \textit{Last-In-First-Out} (LIFO), que determina que a última carga embarcada deve ser a primeira a ser desembarcada \cite{cordeau2010branch}.

No contexto de cadeias de suprimentos em larga escala e operações de logística urbana, o \textit{Dynamic Pickup and Delivery Problem} (DPDP) surge como uma extensão natural e significativamente mais desafiadora do PDP \cite{cai2023survey}. Nesse cenário, as requisições não são conhecidas \textit{a priori}, sendo reveladas de forma contínua e estocástica ao longo do horizonte temporal \cite{hao2022introduction, liu2017dynamic}. Como consequência, o problema exige decisões de despacho e roteamento em tempo real, sob incerteza, o que aumenta substancialmente sua complexidade em relação à versão estática \cite{berbeglia2010dynamic, pillac2013review}.

Além disso, instâncias práticas do DPDP frequentemente incorporam múltiplas restrições operacionais simultaneamente, como janelas de tempo rigorosas, capacidades finitas ou heterogêneas da frota, dinâmicas de docas com tempos de espera não lineares e restrições de carregamento que impõem uma ordem específica de descarregamento, como a política LIFO. Aplicações concretas incluem a entrega de refeições com prazos estocásticos \cite{ulmer2017restaurant}, plataformas colaborativas com \textit{crowdshipping} \cite{stoia2023dynamic} e o despacho industrial de carga em múltiplos terminais \cite{chen2021deepfreight}.

Historicamente, o DPDP tem sido abordado por meio de estratégias de reotimização periódica, utilizando programação inteira mista ou metaheurísticas baseadas em busca local \cite{karami2020periodic, ropke2005adaptive}. Entretanto, o aumento da escala e da dinamicidade do problema torna métodos exatos rapidamente intratáveis, enquanto abordagens puramente heurísticas podem apresentar dificuldades para lidar com ambientes altamente não estacionários. Mais recentemente, técnicas de aprendizado por reforço profundo têm demonstrado resultados promissores em variantes do problema, especialmente em cenários de larga escala \cite{li2021learning, cordeiro2023deep}. Este trabalho se insere nesse contexto e propõe uma abordagem híbrida que combina elementos construtivos e de busca local para abordar o DPDP de forma eficiente dentro das restrições de tempo impostas por ambientes dinâmicos.

O artigo está organizado da seguinte forma: a Seção~\ref{sec:relacionados} apresenta uma revisão da literatura sobre abordagens relevantes para o DPDP. A Seção~\ref{sec:metodologia} descreve a modelagem do problema e os principais componentes do método proposto. A Seção~\ref{sec:resultados} apresenta os experimentos e a análise dos resultados. Por fim, a Seção~\ref{sec:conclusoes} sintetiza as conclusões e aponta direções futuras.

\section{Trabalhos Relacionados} \label{sec:relacionados}

Os primeiros trabalhos sobre DPDP utilizavam estratégias de reotimização periódica, recalculando rotas a intervalos fixos de tempo com base nas ordens reveladas até aquele instante \cite{karami2020periodic}. Embora computacionalmente custosas, essas abordagens produzem soluções de alta qualidade quando o orçamento de tempo é suficiente. No contexto do PDP estático com janelas de tempo, \cite{li2001metaheuristic} propuseram uma metaheurística baseada em busca tabu que se tornou referência para instâncias de médio porte.

A \textit{Adaptive Large Neighborhood Search} (ALNS) \cite{ropke2005adaptive} representou um avanço significativo ao selecionar adaptativamente operadores de destruição e reparo com base em seu desempenho histórico. Variantes mais recentes, como a IALNS-SA \cite{ma2025ialnssa}, incorporam resfriamento simulado para aceitar soluções piores com probabilidade controlada, melhorando a diversificação da busca. A \textit{Variable Neighborhood Search} (VNS) \cite{mladenovic1997variable} é outra metaheurística amplamente aplicada ao DPDP, explorando sistematicamente vizinhanças de crescente amplitude antes de aplicar uma perturbação para escapar de ótimos locais. \cite{cai2022variable} demonstraram que VNS com vizinhanças estruturadas por agrupamentos de pedidos produz resultados competitivos no benchmark ICAPS 2021.

Algoritmos meméticos, que combinam busca evolutiva com refinamento local, também foram explorados no contexto do DPDP real. \cite{zhou2024memetic} propuseram um algoritmo memético com operadores de cruzamento e mutação adaptados à estrutura de precedência do PDP, obtendo resultados de destaque em instâncias dinâmicas de médio e grande porte. Resultados computacionais recentes sobre o mesmo benchmark ICAPS 2021 são reportados em \cite{horvath2025recent}, que servem como ponto de comparação direto para este trabalho.

A aplicação de técnicas de aprendizado por reforço ao roteamento de veículos ganhou força após o trabalho seminal de \cite{kool2019attention}, que demonstrou que modelos de atenção treinados por REINFORCE podem resolver variantes estáticas do VRP de forma competitiva. Antes disso, abordagens baseadas em redes neurais para otimização combinatória haviam sido exploradas por \cite{vinyals2015pointer} com as \textit{Pointer Networks} e por \cite{bello2017neural} com aprendizado por reforço aplicado ao TSP, e também por \cite{nazari2018reinforcement} para o VRP com demandas estocásticas.

\cite{li2021learning} estenderam essa linha de pesquisa ao DPDP industrial, mostrando que políticas aprendidas conseguem generalizar para instâncias não vistas durante o treinamento. \cite{cordeiro2023deep} propuseram uma abordagem baseada em aprendizado por reforço profundo (DRL) para despacho dinâmico com formulação orientada a eventos, permitindo decisões em tempo real sem necessidade de reotimização explícita. Mais recentemente, \cite{jiang2025machine} integraram DRL com teoria de filas para otimizar o roteamento dinâmico de última milha, demonstrando que a combinação de modelos analíticos com aprendizado de máquina pode reduzir tempos de espera e melhorar a utilização da frota.

\section{Metodologia} \label{sec:metodologia}

\subsection{Formulação do Problema}

\subsection{Heurística de Construção}

\subsection{Busca Local}

\section{Resultados} \label{sec:resultados}

\section{Conclusões} \label{sec:conclusoes}

\bibliographystyle{sbc}
\bibliography{sbc-template}

\end{document}
