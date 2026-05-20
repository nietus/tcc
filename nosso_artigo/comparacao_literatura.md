# Comparação com a literatura

## Como comparar corretamente

Não é correto comparar diretamente o valor objetivo do PRMD-ER com os valores dos artigos de E-VRPTW ou UAV routing, porque o nosso experimento:

- adapta os parâmetros para drones;
- adiciona quatro períodos de crescimento;
- compara políticas de ativação de estações;
- usa uma função objetivo penalizada com distância, atraso, rotas e trechos inviáveis.

Portanto, a comparação mais defensável no artigo é contextual:

- benchmark de origem;
- tipo de restrição;
- classe de método;
- escala experimental;
- tipo de evidência reportada.

## Referências principais

### Schneider, Stenger e Goeke

Problema: E-VRPTW.

Método: VNS/TS híbrido.

Resultado relevante:

- 36 instâncias pequenas;
- VNS/TS iguala CPLEX quando CPLEX encontra ótimo;
- tempo médio reportado para VNS/TS nas pequenas: 5,03 s;
- nas instâncias grandes, VNS/TS tem gap médio de 0,35% para a melhor solução conhecida.

Uso no artigo:

Schneider é a referência de benchmark e mostra que VNS/TS é uma escolha forte para roteamento com recarga. O nosso MP-EAVNS segue a mesma família, mas muda o foco para drones, ativação de estações e crescimento multi-período.

### Shi et al.

Problema: UAV routing com janelas de tempo e recarga.

Método: ALNS.

Resultado relevante:

- instâncias criadas a partir de Solomon;
- ALNS comparada com ACO e VNS;
- ALNS reportada como melhor e mais estável.

Uso no artigo:

Justifica fortemente usar VNS/ALNS para UAVs com recarga e sustenta a adaptação de Solomon/E-VRPTW.

### Coelho et al.

Problema: Green UAV routing multiobjetivo.

Método: MILP + matheurística.

Resultado relevante:

- autonomia limitada;
- múltiplas estações;
- sete objetivos;
- análise por Pareto.

Uso no artigo:

Mostra que UAV + recarga + objetivos ambientais já é uma linha consolidada. Nosso trabalho simplifica para uma função penalizada única para permitir comparação experimental direta.

### Ribeiro et al.

Problema: localização-roteamento de UAVs com estações para inspeção de correias transportadoras.

Método: MILP.

Uso no artigo:

Mostra que localização de estações para UAVs é relevante em aplicação industrial brasileira. Ajuda a defender a importância prática da política gradual de estações.

### Vichitkunakorn et al.

Problema: Stocktaking Drone Routing Problem.

Método: ALNS com codificação/decodificação específicas.

Uso no artigo:

É uma referência direta para combinação de roteamento de drones e localização de estações, mas em armazéns e horizonte único.

## Leitura crítica dos nossos resultados

O resultado atual é bom para a fase do TCC porque:

- MP-EAVNS supera GRASP em 16,0%;
- MP-EAVNS supera heurísticas construtivas em mais de 70%;
- a política gradual fica apenas 12,4% acima da disponibilidade completa;
- a sensibilidade de autonomia 60/80/100 mostra comportamento operacional coerente;
- o método pertence à família VNS/ALNS, que é dominante nos trabalhos mais próximos.

O ponto que ainda precisa ser fortalecido:

- reproduzir uma versão E-VRPTW original, sem adaptação para drones, para medir gap contra Schneider;
- ampliar para instâncias de 100 clientes;
- implementar uma ALNS completa como comparação direta com Shi e Vichitkunakorn.

