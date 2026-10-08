# Estado atual — v59

Arquivos atuais em [output/v59](output/v59/), com visualizador e projeto Creality Print
na raiz de `output/`. A árvore atual mantém somente esta versão; revisões anteriores
estão no histórico do Git. O [manual ilustrado](README.md) descreve o desenho atual.

## Configuração

- Carcaça integrada, impressão com traseira Y125 na mesa, construção na direção −Y.
- Câmara 112 × 132 × 111 mm; parede quente de 4 mm; inox de referência 0,3 mm.
- Isolamento com 23 cavidades alongadas, fechamentos a 45° e ponte nominal de 0,4 mm.
- Porta monolítica com ressalto inteiro em V, junta TPU labial retida e junta secundária no corpo.
- Pega externa em dupla hélice circular real, duas curvas, raio de 6 mm,
  volta completa em 36 mm, hastes Ø3,2 mm e travessas Ø2,2 mm.
  Envelope: altura 54 mm, profundidade 15,2 mm e projeção 18,6 mm além da placa.
  Apoios curvos alargam de R1,8 para R4 junto à porta.
  Porta em pé sobre a borda inferior Z=-4, crescimento +Z, conforme as rampas das células; orientação corrigida nos dois 3MF. Revisar brim e suportes externos na hélice. Nenhum corte na porta ou canal TPU.
  O 3MF salvo pelo usuário recebeu a porta DNA, preservando configurações e demais malhas; validação física de gás pendente.
- Fecho central; lingueta liberando a abertura quando girada 90° após afrouxar o manípulo.
- Duas dobradiças M4 × 20 escareadas, porcas metálicas na porta e apoios externos a 45°.
- Rampas internas a 45° nas cavidades atrás das dobradiças e da base da lingueta.
- Rampa externa da lingueta elimina a face plana remanescente; cavidade CO₂ preservada.
- Auditoria final dos apoios inclui ambos os lados da base da lingueta e das dobradiças.
- Suporte removível reforçado, guias abertas, apoio de 6 mm e folga lateral de 0,8 mm por lado.
- Gavetas com base de 3 mm e rebaixo de lâmina de 0,6 mm; nenhum elemento sobre a lâmina.
- Lâminas conferidas: 76 × 26 e 75 × 25 mm, espessuras 0,9, 1 e 1,2 mm.
- Caixinha traseira 70 × 60 × 21 mm, dois M4 × 12 com engate de 4 mm em apoios cegos maciços.
- Mangueira CO₂ Ø6 mm: entrada e passagem interna Ø6,2 mm, boca Ø6,8 mm e furo do inox Ø6,2 mm; encaixe e vedação física pendentes.
- Misturador CO₂ com teto integrado e abertura do sensor; eletrônica acessível pela tampa lateral.

- Ferramental inox: macho maciço com pilotos cegos e contraformas superior/inferior de 24 mm, nervuras de 12 mm e apoio traseiro. Guias Ø2,5 mm para os três furos do inox; chapa 0,3 mm + folga 0,15 mm por face. Modo próprio no visualizador.

## Validação

- Porta em pé: tetos da região central auditados no STL, rampas de 45° e pontes até 2,4 mm na última fileira. Fatiamento da bandeja 2 no Creality Print 7.2.1 concluiu com saída 0 e sem avisos, usando brim de 10 mm e suporte a partir da mesa em configurações de teste separadas; sem ensaio físico.

- Ferramental: três sólidos válidos, sem interseção com o inox; abertura em Z de 0 a 80 mm conferida e visualizador testado em WebGL. Força e retorno elástico pendentes de ensaio físico.
- Corpo único e peças válidas; 59 pares rígidos sem colisão após remover o puxador.
- Faces finais dos tetos auditadas nas duas dobradiças e no fecho: rampas a 45°, pontes restantes ≤0,4 mm.
- Amostra da dobradiça recortada da parede oca real, com ambas as rampas.
- Porta, lingueta, inserção do inox e retirada da caixinha conferidas geometricamente.
- Extração das gavetas a 0, 5, 15, 30, 50, 72 e 80 mm com porta a 110°.
- Apoio inferior e limites laterais das lâminas conferidos; envelope superior de 40 mm livre.
- 38 peças no 3MF completo, compatíveis com a K1C e margem de 5 mm. Macho na bandeja 10 e contraformas nas 35/36, compartilhadas com amostras PC; pelo menos 5 mm entre peças.
- 3MF principal e da v59 atualizados com a porta DNA; ZIP/XML, malha fechada, escala 1:1 e limites K1C conferidos. Abertura nativa e fatiamento da atualização pendentes.
- 3MF com 38 peças em 36 bandejas em escala 1:1, sem G-code; leitura atual das 38 malhas manifold no CLI Creality Print 7.2.1, saída 0, com `--allow-newer-file` para preservar o projeto principal salvo pelo usuário em 7.3. Sem fatiamento.
- Visualizador regenerado com passagem Ø6,2; teste WebGL e controles anterior ao ajuste CO₂. Imagens gerais do manual correspondem à v59.

Relatórios em [output/v59](output/v59/). Os ensaios amplos de roscas/movimento continuam
opcionais em `cad/model.py --check-movements`. TPU com compressão intencional é excluído
da auditoria rígida. As verificações não simulam deformação, resistência ou vazamento.

## Pendências

- 3MF com referências aos perfis genéricos PC/TPU e processo padrão; sem ajustes personalizados de filamento ou velocidades. Selecionar o perfil padrão e ajustar a temperatura no fatiador; sem validação física.
- Fatiamento, calibração dos parâmetros de PC/TPU e ausência de suporte preso nas cavidades fechadas.
- Adesão da porta em pé, suportes externos e testes físicos dos encaixes, roscas e guias.
- Estanqueidade da porta, passagens de fios, conexão de gás e superfícies impressas.
- Ajuste e fabricação da caixa inox; o modelo de referência não é plano de corte de chapa.
- Medidas finais dos conectores, posicionamento do aquecedor, fios e suporte do sensor.
- Desempenho térmico/CO₂, condensação, limpeza e funcionamento operacional.

O alojamento das lâminas é aberto: limita deslizamento enquanto assentadas, mas permite
retirada vertical e não as segura em uma gaveta invertida. Sem validação física ou operacional.
