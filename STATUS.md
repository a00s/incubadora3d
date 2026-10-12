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
  Frente externa plana Y=-16 na mesa, ressalto V para cima. Isolamento redesenhado: 30 canais em duas fileiras, paredes e nervura central de 2 mm, tetos de 45° fechando em +Y com ponte final de 0,4 mm. Revisar suportes externos na hélice. Nenhum corte na porta ou canal TPU.
  O 3MF salvo pelo usuário recebeu a porta DNA, preservando configurações e demais malhas; validação física de gás pendente.
- Fecho central; lingueta liberando a abertura quando girada 90° após afrouxar o manípulo.
- Duas dobradiças M4 × 20 escareadas, porcas metálicas na porta e apoios externos a 45°.
- Rampas internas a 45° nas cavidades atrás das dobradiças e da base da lingueta.
- Rampa externa da lingueta elimina a face plana remanescente; cavidade CO₂ preservada.
- Auditoria final dos apoios inclui ambos os lados da base da lingueta e das dobradiças.
- Suporte removível aberto com H frontal, guias de 10 mm e folga das gavetas de 0,8 mm por lado.
- Gavetas com base de 3 mm e rebaixo de lâmina de 0,6 mm; nenhum elemento sobre a lâmina.
- Lâminas conferidas: 76 × 26 e 75 × 25 mm, espessuras 0,9, 1 e 1,2 mm.
- Caixinha traseira 70 × 60 × 21 mm, dois M4 × 12 com engate de 4 mm em apoios cegos maciços.
- Mangueira CO₂ Ø6 mm: entrada e passagem interna Ø6,2 mm, boca Ø6,8 mm e furo do inox Ø6,2 mm; encaixe e vedação física pendentes.
- Misturador CO₂ com teto integrado e abertura do sensor; eletrônica acessível pela tampa lateral.

- Ferramental inox: macho maciço com pilotos cegos e contraformas superior/inferior de 24 mm, nervuras de 12 mm e apoio traseiro. Guias Ø2,5 mm para os três furos do inox; chapa 0,3 mm + folga 0,15 mm por face. Modo próprio no visualizador.

## Validação

- Porta deitada: todas as cavidades CAD e tetos centrais do STL auditados para +Y; rampas de 45°, ponte final ≤0,4 mm e fechamento transversal conferidos. Fatiamento da bandeja 2 no Creality Print 7.2.1: saída 0, sem avisos, altura 19 mm e 99 camadas. Teste separado com brim de 5 mm e suporte a partir da mesa; 18.745 pontos médios de segmentos de suporte conferidos, nenhum dentro das cavidades. Sem ensaio físico.

- Ferramental: três sólidos válidos, sem interseção com o inox; abertura em Z de 0 a 80 mm conferida e visualizador testado em WebGL. Força e retorno elástico pendentes de ensaio físico.
- Corpo único e peças válidas; 59 pares rígidos sem colisão após remover o puxador.
- Faces finais dos tetos auditadas nas duas dobradiças e no fecho: rampas a 45°, pontes restantes ≤0,4 mm.
- Amostra da dobradiça recortada da parede oca real, com ambas as rampas.
- Porta, lingueta, inserção do inox e retirada da caixinha conferidas geometricamente.
- Extração das gavetas a 0, 5, 15, 30, 50, 72 e 80 mm com porta a 110°.
- Apoio inferior e limites laterais das lâminas conferidos; folga própria do rebaixo conferida; travessas limitam a carga da gaveta inferior a 18 mm sobre a lâmina.
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
- Impressão física da porta com a frente na mesa, suportes externos e testes dos encaixes, roscas e guias.
- Estanqueidade da porta, passagens de fios, conexão de gás e superfícies impressas.
- Ajuste e fabricação da caixa inox; o modelo de referência não é plano de corte de chapa.
- Medidas finais dos conectores, posicionamento do aquecedor, fios e suporte do sensor.
- Desempenho térmico/CO₂, condensação, limpeza e funcionamento operacional.

O alojamento das lâminas é aberto: limita deslizamento enquanto assentadas, mas permite
retirada vertical e não as segura em uma gaveta invertida. Sem validação física ou operacional.

## Fundo interno para conter o inox já dobrado

Nova placa `fundo_interno_inox_5mm`: 109,2 × 129,2 × 5 mm, cantos R4,6.
Contorno 0,6 mm menor por borda que o macho; folga nominal, sem medição da chapa real.
Instalar dentro das laterais, encostada ao fundo traseiro, e colocar a chapa de inox
sobre sua face voltada à câmara. Ocupa Y104,7–109,7; furo Ø14 em X60/Z116.
Não substitui o fundo de inox. Imprimir deitada, preenchimento 100%, bandeja 37.
STL/STEP na v59 e inclusão nos dois projetos completos. Encaixe físico pendente.
Regenerar com `python cad/rear_insert.py` (exportação e inclusão inicial no 3MF).

## Restrição física — borda fina da entrada quebrada

Na montagem física, o usuário informou que a pequena borda da entrada da porta
quebrou por fragilidade. Para alterações futuras, considerar essa borda ausente:
nenhum novo encaixe, apoio, retenção ou posicionamento pode depender dela.
O apoio frontal do inox deve manter sua largura de forma independente dessa borda.
A foto não define o contorno exato da fratura; o CAD ainda contém a geometria nominal.

## Suporte aberto com H frontal — substitui o suporte com painéis

- Frente H: 110,1 × 129,7 mm, profundidade 12 mm; colunas de 3,15 mm.
- Travessas frontal e intermediária em Z65–71, com cantos R0,8 e reforços locais nas uniões inferiores.
- Seis guias abertas; colunas intermediárias e traseiras locais e seis pés apoiados no piso de inox.
  Sem painéis laterais e sem travessas transversais atrás.
- Frente em Y3,6, sem depender da borda quebrada da entrada; folga nominal do inox
  de 0,15 mm por lado. Gavetas e níveis originais preservados.
- A moldura frontal separada anterior foi substituída pelo H integrado e removida
  do projeto de impressão. Fundo traseiro de 5 mm preservado.
- Limpeza: conjunto removível pela frente, sem ferramentas ou cola; retirar para
  expor o inox e limpar separadamente as guias abertas.
- Peso admissível, pressão real no inox e facilidade de retirada ainda não ensaiados.
- Auditoria CAD completa: 60 pares rígidos sem colisão; extração das gavetas e
  encaixes originais conferidos. Projeto principal e cópia v59 com 39 peças em
  36 bandejas; suporte na 4, fundo traseiro na 13 conforme disposição salva pelo usuário.
- STL/STEP individuais, conjunto STEP, visualizador e cópia servida na porta 8081 atualizados.

## Apoios das gavetas alargados

Os seis apoios passaram de 6 para 10 mm de largura útil, com sobreposição mínima
nominal de 8,4 mm sob as gavetas no limite da folga lateral de 0,8 mm.
Gavetas, altura dos apoios e H frontal preservados. Batentes traseiros acompanham
a nova largura. A colocação e o deslizamento precisam ser confirmados na impressão.

## Travessas na altura central, na frente e no meio da profundidade

Dois H com travessas em Z65–71 mm (1 mm abaixo da segunda gaveta), um frontal
em Y3,6–15,6 e outro intermediário em Y37,55–49,55. Colunas de altura integral
no meio também apoiam as laterais do inox. Apoios de 10 mm das gavetas preservados.
A travessa interna limita a altura de carga sobre a lâmina inferior: 18 mm livres
para lâminas de até 1,2 mm, com envelope contínuo de retirada conferido.
As verificações anteriores de 40 mm referiam-se à própria gaveta e seu rebaixo,
e não representam espaço de carga disponível no conjunto montado.

## Redução do suporte para expor mais inox

- Travessas de afastamento preservadas em Z65–71, na frente e no meio; seção 8 × 6 mm.
- Colunas encurtadas até Z104 (base da gaveta superior), profundidade 6 mm na frente
  e no meio e 4 mm atrás, largura 3,15 mm. Sem prolongamentos até o teto.
- Seis trilhos de 10 mm preservados; colunas e pés com cantos R0,6.
- Sem painéis, fundo plástico ou novas cavidades; remover o conjunto para expor e
  limpar o inox atrás dos apoios.
- Passagem das gavetas, apoios mínimos de 8,4 mm e limite de carga de 18 mm sobre
  a lâmina inferior mantidos. Peso admissível e encaixe dependem de teste físico.
- Volume CAD reduzido de 56.649,7 para 37.945,0 mm³ (33%); envelope do suporte
  110,1 × 79,9 × 99,05 mm. Cotas do visualizador isolado corrigidas para a peça,
  sem exibir as medidas globais do corpo.
- Auditoria CAD atual: 59 pares rígidos sem colisão, apoios e passagem conferidos.

## Centro sem sobras ou pontos de engate na entrada

- Pé intermediário removido; quatro pés locais somente na frente e atrás.
- Colunas intermediárias limitadas a Z40–101, entre os trilhos inferior e superior,
  sem prolongamentos acima ou abaixo. Reforços diagonais removidos.
- Travessas de afastamento em Z65–69, seção 6 × 4 mm, com a mesma profundidade
  das colunas: sem degraus salientes nas junções. Folga de 3 mm sob a segunda gaveta.
- Apoios de 10 mm e folga lateral das gavetas preservados; carga útil de 18 mm
  sobre a lâmina inferior mantida. Facilidade de colocação física ainda por testar.

## Bucha redonda do sensor CO₂

- Substituído o anel espesso por manga de parede 0,6 mm, dois lábios internos
  de 0,55 mm e dois externos de 0,5 mm, com entrada chanfrada.
- Furo impresso Ø20,4 mm e posição de apoio do sensor preservados. Corpo
  Ø19,8 mm; lábios internos livres Ø15,4 mm; externos Ø20,6 mm.
- Atualizados STL, STEP, bucha e duas amostras no 3MF completo, preservando
  configurações salvas. Conferência física de encaixe e vedação pendente.
- Suporte sem pés intermediários, pontas ou reforços diagonais. Borda superior
  lateral contínua de 1,5 mm mantém a retenção da gaveta superior.

## Passagens dos fios com rolhas labiais bipartidas

- Aquecedor atualizado para dois fios Ø1,42 mm e sensor lateral de umidade/
  temperatura para três fios Ø1,40 mm.
- Duas metades por rolha, divisão pelos eixos dos fios, dois lábios finos
  de 0,4 mm por fio e dois lábios externos para o furo existente Ø12 mm.
- Inserção de 13,7 mm na parede de 14 mm; face interna recuada 0,3 mm, flange
  somente externa Ø16 × 1,5 mm. Corpo impresso preservado.
- STL/STEP pareados com metades separadas por 4 mm e flange na mesa.
  Montagem no STEP completo e no visualizador mantém as posições físicas.
- Encaixe, compressão da junta entre metades e vedação dependem de ensaio físico.
- Projeto completo: pares nas bandejas 11 (aquecedor) e 12 (sensor), com
  configurações anteriores preservadas. Duas malhas fechadas separadas por 4 mm
  em cada par; limites e referências das 36 bandejas conferidos.
- Auditoria do conjunto: 59 pares rígidos sem colisão. STL do corpo permanece
  idêntico ao anterior; visualizador servido na porta 8081 atualizado.

## Furo lateral do plugue do aquecedor Ø10,68 mm

- Ampliado de Ø8 para Ø10,68 mm o furo lateral da caixinha externa parafusada
  do aquecedor, mantendo centro, dimensões externas e fixações M4×12.
- Atualizados STL, STEP individual, conjunto STEP, projeto 3MF completo e
  cópia versionada, com configurações salvas preservadas.
- Conferir o encaixe do plugue real na peça impressa.
- Furo medido nas duas faces do STEP: Ø10,68 mm; caixinha válida com um sólido.
  Bandeja 9 preservada; limites K1C e 59 pares rígidos sem colisão conferidos.
