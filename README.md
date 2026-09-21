# Mini incubadora CO₂ — estudo v0.31

Modelo preliminar para revisar montagem e dimensões. **Ainda não liberado para impressão funcional.**

## Versão atual

Usar `output/v31/`. As seções antigas abaixo documentam o histórico;
a revisão v0.31 ao final descreve a configuração atual.

## Visualizar e ajustar

Abra `output/visualizador.html` no navegador (funciona sem servidor ou conexão).
O fragmento `output/incubadora-3d.html` é a versão embutida na conversa.
Arraste para girar; use Abrir porta, Zoom e Retirar bandejas.
Ative Corte das paredes e porta e arraste Altura do corte (−10 a 150 mm).
O corte mostra o material das paredes e preserva as cavidades internas.
Em Peças, marque/desmarque cada componente ou use Isolar / Mostrar todas.
Selecione Fecho → Afrouxado e girado 90° para liberar o controle de abertura.
A retirada das bandejas fica bloqueada com a porta abaixo de 90°.
O detalhe Encaixe da junta TPU mostra o corte do perfil, derivado das mesmas
coordenadas usadas no CAD.
O destaque da passagem de gás é apenas uma indicação geométrica; não é peça impressa.

## Geometria inicial — histórico v0.8

- Câmara principal: 120 × 115 × 140 mm, parede nominal 4 mm.
- Misturador semicilíndrico lateral: raio externo 32 mm, altura 110 mm,
  unido ao corpo e compartilhando a parede lateral. Tampa removível separada.
- As duas câmaras ocupam 152 mm na largura; dobradiças ultrapassam essa cota. A base separada foi removida; o próprio
  fundo do corpo apoia o conjunto.
- Passagem direta Ø8 mm pela parede comum, centro em y=60, z=34 mm.
  Não requer mangueira entre as duas câmaras. Entrada externa de gás e escape
  traseiro continuam necessários; os furos reservados não são conexões finalizadas.
- Cantos principais internos R6, externos R8; reservatório com fundo arredondado,
  bordas e aberturas das bandejas arredondadas. Misturador com transições internas
  arredondadas. Trilhos, dobradiças e detalhes ainda exigem revisão de limpeza.
- Três bandejas, com uslides de referência 80 × 30 mm; dimensões reais pendentes.
- Porta com duas dobradiças à direita, pinos nominais Ø3 mm em furos Ø3,4 mm.
  Duas linguetas giratórias à esquerda apoiam na frente da porta. Para abrir:
  afrouxar os manípulos (deslocamento ilustrativo de 0,8 mm), girar as linguetas
  90° e abrir a porta. Para fechar: encostar a porta, retornar as linguetas e
  apertar os manípulos manualmente. Os parafusos permanecem montados.
- Linguetas e manípulos são peças imprimíveis separadas; parafusos M4 com cabeça
  sextavada e porcas metálicas são ferragens. As porcas têm alojamento sextavado
  no corpo; a cabeça do parafuso encaixa no manípulo. Medidas e comprimento final
  da ferragem pendentes de protótipo; roscas não estão modeladas.
- Borda frontal reforçada: faixa de vedação com 8 mm, profundidade de 8 mm.
- Junta TPU contínua, removível, com pé retido mecanicamente e lábio externo.
  Canal com chanfro de entrada e garganta estreita: 2,4 mm; cavidade interna
  4 mm de largura, 3,2 mm de profundidade. Pé TPU 3,5 mm, com ponta chanfrada.
  A junta é pressionada pela frente, aos poucos, para o pé passar pela garganta.
  Não usa cola. Essas medidas são de ensaio, não tolerâncias de produção.
- Lábio livre saliente 1,5 mm; a face interna da porta fechada fica a 1 mm da
  carcaça, correspondendo a 0,5 mm de interferência nominal. O modelo mostra
  TPU sem deformação; a rigidez, esforço de aperto e estanqueidade precisam de teste.

### Teste pequeno do encaixe

Imprimir `output/v04/amostra_canal_rigido.stl` no material do corpo e
`output/v04/amostra_junta_TPU.stl` no TPU real, antes da junta inteira.
As amostras têm 35 mm de comprimento e usam exatamente o perfil do modelo.
Estão orientadas com base no plano Z=0; canal voltado para cima, TPU com pé
apoiado. Testar encaixe pressionando pela frente, retenção ao puxar, retirada
para limpeza e compressão do lábio. Essa amostra não testa vazamento nos cantos
nem a vedação de uma porta completa. Ajustar os perfis GROOVE, FOOT e LIP em
`cad/model.py` após o ensaio. Dureza do TPU, bico e calibração ainda desconhecidos.

## Arquivos e geração

```
.venv/bin/python cad/model.py
python3 cad/build_viewer.py
```

CadQuery fixado em `requirements.txt`. Os parâmetros de referência estão em
`cad/model.py`; alguns detalhes ainda usam medidas fixas deste estudo.
`output/v31/` contém o STEP, STL separado de cada peça imprimível e `pecas.json`,
que distingue impressão, ferragens e referências. Os STL conservam as coordenadas
da montagem; orientar e posicionar no fatiador após definir material e suportes.
As pastas `output/v02/` a `output/v27/` preservam revisões anteriores; **usar os STL em `output/v31/`**.

`python3 cad/build_viewer.py` atualiza tanto o fragmento quanto
`output/visualizador.html`, sem dependências externas no navegador.

## Verificações efetuadas

O gerador verifica sólidos válidos com volume positivo, corpo integrado como um
único sólido, passagem de gás desobstruída e ausência de interseção porta/corpo
nos ângulos 0°, 30°, 60°, 90° e 110°, incluindo as linguetas liberadas.
Também verifica que o pé da junta cabe no corpo sem interseção e que as duas
amostras são sólidos válidos. A compressão intencional do lábio não é simulada. Não é uma análise mecânica de esforços nem
uma garantia de movimento com tolerâncias reais de impressão.

## Fluxo e limitações

Ar + CO₂ dosados → mistura/sensor → passagem na parede → câmara → escape.
Uslides com laterais abertas à atmosfera comum; sem injeção direta nos slides.
Recipiente de reação externo; a câmara impressa não é reservatório pressurizado.
A parede compartilhada e a passagem direta permitem troca de calor e umidade;
não se pode assumir proteção do sensor contra condensação nesta arquitetura.
A leitura na mistura não confirma a concentração no interior dos slides.

Uma válvula de retenção pode exigir pressão diferencial relevante para abrir.
Selecionar escape após conhecer vazão máxima, pressão de abertura, perda de carga
e condensação. Não há pressão segura para as células estabelecida neste projeto.
A saída operacional não substitui proteção independente contra sobrepressão.
Validar sem culturas, medindo pressão diferencial junto às bandejas.
Referência: https://www.theleeco.com/uploads/2021/04/IMH-8th-Edition-2020.pdf

## Pendências para protótipo funcional

- Medidas reais dos uslides, aquecedor, sensor, mangueiras e mesa da impressora.
- Confirmar filamento e material da junta (possivelmente TPU).
- Retenção axial dos pinos, interface do sensor (suporte e vedação próprios).
- Tolerâncias, resistência das abas de fecho, compressão uniforme da junta.
- Aquecedor, proteção térmica independente, isolamento e passagens elétricas.
- Limpeza dos canais e superfícies impressas; cantos arredondados não eliminam
  a rugosidade das camadas nem validam descontaminação.
- Estanqueidade, condensação, uniformidade térmica e resposta do CO₂.
  Nenhuma simulação térmica ou de escoamento foi realizada.


## Tampa do misturador — revisão v0.4

A tampa removível em D tem 6 mm de espessura e três furos passantes para M4.
Uma flange de raio externo 46 mm, com 8 mm de espessura, faz parte do corpo.
Parafusos e arruelas comprimem a tampa contra uma junta contínua de TPU;
porcas sextavadas ficam em alojamentos acessíveis pela parte inferior da flange.
Os três parafusos ficam fora do contorno da junta. Não há rosca impressa.
O conjunto agora ocupa 166 mm de largura incluindo a flange (sem ferragens).

A junta da tampa usa o mesmo perfil de retenção da junta frontal, aplicada a um
contorno em D: chanfro de entrada, garganta 2,4 mm e pé TPU 3,5 mm. Encaixar
progressivamente pela parte superior; pode ser removida para limpeza, sem cola.
Apoios rígidos de 1 mm nos parafusos limitam o fechamento. O lábio livre saliente
1,5 mm tem interferência nominal de 0,5 mm; sua deformação não foi simulada.

Para desmontar: interromper a alimentação de gás, despressurizar pelo escape,
retirar os três parafusos e arruelas e levantar a tampa. O controle Retirar tampa
do misturador mostra essa separação. A junta permanece no canal, podendo ser
ocultada/isolada na lista. Porcas, parafusos e arruelas são referências de ferragem,
sem exportação como peças de impressão. A tampa e a junta têm STL independentes.

A abertura livre fica com aproximadamente 24 mm de largura máxima no sentido X;
a flange deixa acesso superior ao interior, mas a remoção de suporte nas curvas
e no canal precisa ser comprovada no fatiador/protótipo. A passagem interna de gás
continua Ø8 mm e não serve como acesso amplo de limpeza. Revisar a orientação e
os suportes antes de imprimir o corpo completo.

O furo Ø16 mm do sensor continua sendo uma reserva geométrica: falta o modelo real
para projetar suporte e vedação específicos. Não considerar a montagem estanque
com esse furo sem tratamento. A pressão máxima não foi informada; nenhum limite
de pressão, torque ou resistência foi certificado. A fixação da tampa não substitui
escape e alívio de pressão. Não armazenar o gás da reação no corpo impresso.

Verificação adicional: junta da tampa como sólido contínuo sem interseção com o
corpo e tampa removível verticalmente, sem interferência com o corpo nas posições
0, 5, 20 e 40 mm de elevação. A vedação, flexão da tampa, resistência da flange e
retenção das porcas ainda dependem de ensaio.

Relato do usuário: gás liberado em pulsos, com algumas gotas a cada poucos
segundos; pressão não medida. Frequência de gotas não define pressão máxima nem
pico de pressão. Não foi atribuído limite de pressão admissível à tampa.


## Histórico: paredes com cavidades de ar — revisão v0.5

O recorte lateral descrito nesta seção foi eliminado na v0.6; veja abaixo.

Corpo e porta foram engrossados para fora; não é necessário preencher com espuma
ou montar painéis externos. O corpo permanece um sólido imprimível; a porta também.
Extensão nominal 10 mm, com peles de 2 mm e pequenas células de ar, geralmente
6 × 18 × 20 mm (menores onde o espaço é menor), separadas por nervuras. Cobertura
nas paredes direita e traseira, teto e fundo. Na esquerda há recorte de acesso
para o misturador e a remoção vertical da tampa: essa região permanece sem a
camada adicional. A parede compartilhada com o misturador não foi alterada.
A tampa e a parede externa curva do misturador continuam na construção anterior.

Na porta, a região central de 87 × 120 mm ganhou a camada de 10 mm; ali a
espessura total é 15 mm. O perímetro, fechos, dobradiças e região do puxador
continuam maciços e sem espessamento para manter as folgas. Portanto existem
pontes térmicas nessas regiões. Nenhum desempenho térmico foi simulado.

As células têm teto inclinado, reduzindo o vão de fechamento em impressão com o
corpo na vertical. Isso não constitui validação de impressão sem suporte: revisar
as prévias de camadas, especialmente teto externo, canais de TPU, flange e porta.
Não gerar suportes dentro de cavidades fechadas. Testar uma amostra antes do corpo.
A borda das células cortadas pelo recorte do misturador recebeu fechamento sólido.
Os dois furos traseiros atravessam a parede nova com mangas sólidas, sem comunicação
intencional com o isolamento. Os volumes internos funcionais foram preservados.

O controle Corte das paredes e porta mostra seções reais do CAD a z=70 mm.
As seções não são peças novas e não geram STL nem entram no STEP da montagem.

### Compatibilidade dimensional Creality K1C

Volume oficial 220 × 220 × 250 mm:
https://www.creality.com/products/k1c-carbon-3d-printer

O script `python3 cad/check_k1c.py` lê os STL exportados, verifica a caixa envolvente
de cada peça com margem de 5 mm por lado em XY e centraliza cópias individuais em
`output/v05/k1c_posicionados/`, com Z mínimo igual a zero. Não escolhe suportes nem
orientação ótima; não são arquivos de máquina. Relatório: `compatibilidade_k1c.json`.
Corpo completo: 177 × 135 × 160 mm; porta com dobradiças/puxador: 131 × 19 × 140 mm.
Todas as peças atuais e as duas amostras cabem individualmente nessa verificação.
A compatibilidade não significa que toda a montagem caiba numa única impressão.
Filamento rígido e dureza do TPU ainda precisam ser informados.


## Correção da lateral do CO₂ — v0.6

A camada de 10 mm com células de ar agora cobre também toda a lateral esquerda
externa da câmara aquecida. O recorte de acesso da v0.5 foi removido. O misturador,
a tampa, a junta, a entrada de gás, o sensor e as ferragens da tampa foram deslocados
10 mm para fora, preservando os volumes úteis e o acesso vertical da tampa.
A ligação de gás continua impressa no corpo: canal Ø8 mm, atravessando uma manga
sólida Ø12 mm entre x=-10 e x=4. A manga isola o circuito de gás das células de ar.

Cobertura adicional nas duas laterais, fundo, teto e parede traseira; porta com
cavidades na área central. Bordas de vedação, nervuras, ferragens e passagem de gás
continuam formando ligações sólidas locais. Não foi alegado isolamento perfeito
nem ausência de perda térmica. O misturador não faz parte da região aquecida isolada.

Verificados: sólidos válidos, corpo único, pontos livres na camada de ar esquerda
em três alturas, canal de gás livre, encaixes de TPU, retirada vertical da tampa e
abertura da porta nos ângulos amostrados. Nenhuma simulação térmica foi feita.

Corpo completo 187 × 135 × 160 mm; permanece compatível dimensionalmente com K1C
220 × 220 × 250 mm, incluindo margem XY de 5 mm por lado. Arquivos atuais:
`output/v06/`. Executar `python3 cad/check_k1c.py` após gerar o modelo para atualizar
as cópias centralizadas e o relatório dimensional.


## Correção do painel da porta — versão atual v0.7

A extensão isolante agora acompanha toda a face de 120 × 140 mm da porta,
com os mesmos cantos arredondados. Foram eliminadas as faixas laterais de
17 mm e as faixas superior/inferior de 10 mm sem a camada adicional.
O painel completo tem 15 mm de espessura, com células de ar fechadas e borda
perimetral de 2 mm para fechar as células. Nervuras, dobradiças e ligações
mecânicas continuam sólidas localmente. Não existe isolamento térmico perfeito.

Puxador, linguetas e manípulos foram deslocados 10 mm para a frente. Os apoios
fixos foram prolongados e os envelopes dos parafusos ajustados. A seleção do
comprimento comercial e a resistência das ferragens continuam pendentes.
As posições da junta e do eixo das dobradiças foram preservadas.

O gerador verifica uma porta sólida única, amostras de cavidade perto de ambas
as laterais, do teto e do fundo da porta, e ausência de colisões porta/corpo e
porta/linguetas liberadas de 0° a 110°, em passos de 5°. A geometria do painel
é mostrada pelo mesmo controle Corte das paredes e porta. Conferir orientação
e pontes no fatiador antes de imprimir. Sem ensaio de desempenho térmico.
Arquivos desta revisão: output/v07/.

Dimensões verificadas na v0.7: corpo 187 × 141 × 160 mm; porta com puxador e dobradiças 131 × 29 × 140 mm. Todas as peças STL cabem individualmente na K1C com margem XY de 5 mm por lado.

## Entrada de CO₂ — v0.8
Entrada integrada à parede curva traseira do misturador, na altura de 18 mm.
Substitui o furo genérico anterior por espigão para mangueira de silicone com
Ø interno informado de aproximadamente 4,5 mm. Haste Ø4,6 mm, dois ressaltos
suaves Ø5,0 mm, ponta cônica e passagem interna Ø2,6 mm. Trecho de encaixe
13 mm após a base reforçada Ø10 mm. Não necessita cola no desenho.
Dimensões de interferência preliminares: testar com a mangueira real antes
 de imprimir o corpo, sem presumir retenção ou estanqueidade.
A amostra `output/v08/amostra_entrada_CO2_4p5mm.stl` reproduz o espigão
horizontal do corpo. Conferir suportes e desobstrução do canal no fatiador.
Este conector não regula pressão nem substitui escape/alívio.
Arquivos atuais em `output/v08/`.

Sensor informado: cilindro Ø15,62 × 80,75 mm inserido abaixo da tampa; ponta no Z30,25 mm. Entrada horizontal no Z18 mm, 12,25 mm abaixo da ponta. Furo provisório Ø16,4 mm para folga; retenção/vedação do sensor ainda pendentes da medida do colar e da região de apoio. Cabeça externa ainda aproximada. A posição baixa não constitui separador de líquido.

## Caixa da eletrônica — v0.9
Caixa seca separada na traseira, ao lado do misturador. Dimensões externas
44 × 42 × 112 mm (46 × 45 × 112 mm incluindo abas); espaço interno 39 × 39,5 × 107 mm (antes de pilares e suporte).
Placa de 43,12 × 25,16 mm na vertical; suporte preliminar com batentes e rasgos
para cintas removíveis. Componentes, conectores e furos reais ainda não medidos.
Tampa traseira com quatro M3 e porcas cativas; caixa fixada em duas abas externas
por M3 e porcas cativas, sem atravessar a parede da câmara ou seu isolamento.
Ferragens dessa caixa ainda não representadas; comprimentos finais a definir.
Entrada lateral de cabo Ø7 mm provisória. Adaptador RJ45 removível com quatro
furos Ø2,4 mm para ferragens M2: placa cega até medir corpo e travas do conector.
A abertura maior da tampa recebe o adaptador; não é o encaixe direto do RJ45.
O acesso de manutenção ocorre retirando a tampa traseira. Ocultar a tampa e o
adaptador no visualizador permite conferir a placa e seu espaço.
Não foi verificada a temperatura dessa caixa; ela não é estanque.
Arquivos atuais: output/v09/. As medidas do colar do sensor continuam pendentes:
os 4,5 mm informados precisam ser esclarecidos e não foram aplicados ao sensor.

## Corpo único, sensor e RJ45 — v0.10
O alojamento da eletrônica agora é parte do `corpo_integrado.stl`, unido à
pele externa por uma parede contínua. Não há peça separada nem parafusos de
fixação da caixa ao corpo. Tampa de manutenção e adaptador RJ45 continuam
removíveis. Volume de gás e alojamento da eletrônica permanecem separados.
Corpo completo: 187 × 186 × 160 mm. Validar orientação e suportes no fatiador.

RJ45: adaptador de teste com recorte 14,79 × 19,31 mm, espessura 1,6 mm,
conforme ficha CommScope KJ610-BK (não é identificação do conector do usuário):
https://www.commscope.com/globalassets/digizuite/76511-p360-2291216-2-external.pdf
Usar `amostra_encaixe_RJ45.stl` para testar retenção antes de imprimir o conjunto.

Sensor: fotos indicam cabeça de 20,55 mm, colar aproximadamente Ø18,31 mm e
corpo Ø15,55 mm; preservado Ø15,62 mm como maior diâmetro medido anteriormente.
Altura do colar 2,5 mm e altura/profundidade da cabeça continuam aproximadas.
Bucha TPU removível: furo livre Ø15,3 mm; região externa Ø20,6 mm em furo rígido
Ø20,4 mm; aba superior Ø24 mm e aba inferior cônica até Ø22 mm. A interferência
é intencional e não há simulação de deformação ou garantia de vedação/retenção.
Amostras de bucha Ø15,3 e Ø15,5 mm e amostra rígida da tampa disponíveis.
Montagem: encaixar bucha na tampa e inserir sensor até o colar apoiar na aba.
Confirmar que a bucha só abraça a parte lisa, sem cobrir as janelas do sensor.
Inserção 80,75 mm referida provisoriamente ao apoio do colar: ponta Z37,75 mm;
entrada CO₂ Z18 mm, abaixo da ponta. Não constitui proteção contra líquido.
Arquivos atuais: output/v10/.

## Layout lateral compacto e passagens elétricas — v0.11
A eletrônica ocupa X-56..-10, Y94..125, Z5..100, na mesma lateral do misturador,
sem prolongar a traseira. A tampa fica embutida em Y122..125. O adaptador RJ45
fica na face lateral X-56, com eixo de inserção X e região reservada acima da PCB.
Interior antes de suportes: 41 × 25,5 × 90 mm. A profundidade é menor que na v0.10;
altura dos componentes e curvatura dos fios ainda precisam ser conferidas.
Não existem abas ou suportes externos para prender a caixa: é parte do corpo.

Passagens separadas: teto para três fios do sensor e traseira para dois fios do
aquecedor. Cada passagem possui manga sólida Ø16, furo Ø12, TPU bipartido com
abas e duas metades rígidas de compressão. Quatro M3 e porcas cativas por passagem;
ferragens e comprimentos finais pendentes. Furos de fixação cegos em reforços
sólidos, sem comunicação com o gás. A manga isola o canal das células de ar.
TPU livre Ø12,2 mm no pescoço, aba superior Ø20 × 2 mm; tampa comprime nominalmente
0,4 mm. Encontro das metades e compressão radial precisam de ensaio físico.
Canais provisórios para fios isolados Ø1,6 mm (sensor) e Ø2,4 mm (aquecedor),
sem interferência dimensionada até receber medidas. Não alegar estanqueidade.
Sensor de temperatura/umidade: apenas envelope e posição superior; fixação pendente.
Película 90 × 33 mm e chapa metálica de 1 mm são referências, sem fixação ou ensaio.
Conector externo de alimentação permanece separado da eletrônica de comunicação;
seu alojamento depende do diâmetro e comprimento da rosca. Ainda não modelado.
Arquivos atuais: output/v11/.

## Medida dos fios do aquecedor — v0.12
Película confirmada pelo usuário: 90 × 33 mm. Dois fios com isolamento Ø1,68 mm.
Canais de TPU ajustados para Ø1,60 mm, interferência diametral nominal de 0,08 mm;
valor inicial para teste, sem validação de vedação ou deformação do isolamento.
Sensor usa conector removível. TPU e prensas são bipartidos: desmontar as duas
metades libera o furo rígido Ø12 mm para passar a cabeça do conector.
Dimensões do conector e dos fios do sensor pendentes; não garantir sua passagem
ou vedação até medir. Não é necessário soldar para abrir a vedação.
Arquivos atuais: output/v12/.

Correção confirmada: conector do sensor permanece dentro da incubadora; apenas
três fios Ø1,36 mm atravessam a vedação. Canais TPU Ø1,30 mm (interferência
nominal diametral 0,06 mm) para teste. A passagem não precisa acomodar o conector.
Mantidas as duas metades removíveis para manutenção sem cortar os fios.

## Gavetas afastadas do aquecedor — v0.13
Profundidade das três gavetas reduzida de 96 para 72 mm, retirando 24 mm atrás.
Borda traseira fechada em Y80; chapa de referência começa em Y106: folga geométrica
26 mm. Apoios do uSlide e sua posição mantidos; abertura central encurtada para
46 mm para preservar a travessa traseira. Trilhos terminam em Y82,5 e incluem
batentes em Y80,5, com folga nominal de 0,5 mm para a gaveta fechada.
A distância é uma decisão geométrica inicial, não uma validação térmica.
Inclui ajuste anterior: sensor 3 fios Ø1,36/canais Ø1,30; aquecedor 2 fios
Ø1,68/canais Ø1,60, todas as vedações ainda para teste. Conector do sensor interno.
Arquivos atuais: output/v13/.

Aquecedor representado em pé na traseira: 90 mm na vertical e 33 mm na horizontal, entre Z18 e Z108.

## Espigão acessível e lateral contínua — v0.14
Espigão reposicionado na face lateral X-56, em Y60/Z18, apontando para -X;
ponta em X-70. Manga sólida liga diretamente a parede do misturador ao espigão,
sem comunicar o gás com o espaço vazio da carenagem. Entrada antiga removida.
Carenagem integrada com pele de 2,5 mm une visualmente mistura e eletrônica;
recorte interno preserva a câmara de mistura. Não é uma peça adicional para imprimir.
Largura máxima com espigão 201 mm, incluindo os 14 mm que saem da face lateral.
Inclui gavetas de 72 mm, batentes e afastamento de 26 mm da chapa traseira,
aquecedor em pé 90 mm na vertical, e vedações para as medidas de fio informadas.
Arquivos atuais: output/v14/.


## Montagem e passagens revisadas — v0.15

- Espigão CO₂ recolhido sob a lateral, orientado para trás, com passagem interna em L.
- Removidos os dois furos traseiros genéricos; escape/alívio permanece pendente.
- RJ45 encaixa diretamente na parede lateral (recorte de referência 14,79 × 19,31 mm,
  parede local de 1,6 mm), sem moldura externa. Validar com a amostra.
- Cobertura superior removível protege a cabeça do sensor e o percurso dos fios.
  Retirar seus dois parafusos traseiros antes de levantar a tampa do misturador.
  Altura da cabeça e espaço de dobra dos fios ainda precisam de confirmação física.
- Três canais laterais de 7,4 × 4 mm permitem inserir as porcas M4 com pinça,
  com a cobertura retirada. Os alojamentos sextavados evitam rotação; inserir as
  porcas antes dos parafusos da tampa. Conferir folgas com a impressão real.
- Passagem traseira dos dois fios Ø1,68 mm em X60/Z116, próxima da saída superior
  da película vertical de 90 × 33 mm. Compartimento separado para a alimentação
  12 V imediatamente atrás, com tampa removível. Furo do conector permanece
  pendente do diâmetro e comprimento da rosca; potência/corrente não informadas.

Arquivos atuais: output/v15/. As seções anteriores registram versões anteriores.
Validação geométrica e envelope de impressão não substituem ensaio de montagem,
vedação, retenção das porcas, desempenho térmico e verificação no fatiador.


## Acesso ao sensor e caixa de alimentação compacta — v0.16

Substitui a cobertura grande por um tampo estreito de 18 mm, aberto na frente e
encaixado por dois pinos cônicos. Cabeça e parafusos do sensor ficam expostos.
Puxar o tampo para cima antes de desmontar a tampa do misturador. Encaixe nominal
e retenção devem ser ajustados com impressão de teste; não são uma vedação.

Caixinha do conector reduzida para 40 × 18 × 34 mm externos, além de tampa de
2,5 mm. A largura acomoda a prensa bipartida existente dos fios. Furo redondo
Ø8 mm provisório alinhado à passagem traseira do aquecedor. Confirmar diâmetro
e comprimento da rosca e profundidade do conector antes de imprimir; espaço
remanescente é para uma sobra curta de fio, não uma bobina de cabo.

Arquivos atuais: output/v16/.


## Cápsula lateral destacável do aquecedor — v0.17

A caixa de alimentação deixou de ser fundida à carcaça. Cápsula arredondada
44 × 21 × 34 mm, impressa separadamente, com furo Ø8 mm voltado para +X
(lateral direita). Rebaixo Ø14 mm deixa parede local de 2,5 mm para a rosca.
O Ø8 mm foi autorizado pelo usuário para a primeira impressão de teste.

Suporte separado reutiliza os quatro parafusos da prensa do aquecedor,
acrescentando 2,4 mm à espessura de aperto: escolher o comprimento dos M3
considerando essa espessura e o engate nas porcas existentes. Instalar uma
porca M2 no suporte pela face voltada à carcaça antes de fixá-lo. A cápsula
desliza de cima para baixo nos dois trilhos T (folga nominal 0,25 mm por lado),
e um M2 de aproximadamente 25 mm, acessível pela traseira, impede que suba.
Conferir comprimento do parafuso e retenção na montagem de teste.

Montar o conector e sua porca pela abertura da cápsula antes de encaixá-la.
A passagem vedada dos fios continua independente da cápsula; desligar a fonte
antes de desmontar. O tamanho real do conector e a curva dos fios continuam
sujeitos ao teste. Arquivos atuais: output/v17/.


## Alimentação simplificada — v0.18

Substitui o conjunto v17 por uma única bucha TPU e uma caixinha separada
36 × 21 × 30 mm. Retirados suporte, trilhos, parafuso de retenção e as duas
prensas do aquecedor. A caixinha possui dois pinos cônicos integrais, de 2 mm
de comprimento e Ø2,4 mm máximo, encaixados em furos cegos da carcaça com
reforço local. Retenção por ajuste; validar na impressão de teste.

O furo Ø8 mm está no lado direito de quem olha a traseira (-X no modelo),
com parede de 2,5 mm. Instalar o plugue e sua porca pela face aberta antes de
encaixar a caixa. Passar os dois fios na bucha TPU antes de ligá-los ao plugue.
A bucha tem abas de retenção e canais Ø1,60 mm para fios medidos Ø1,68 mm,
sem compressão por parafusos; vedação ainda não ensaiada.

Arquivos atuais: output/v18/. Grupos de seleção mantidos no visualizador.


## Saída lateral superior do sensor — v0.19

Sensor de temperatura e umidade movido para junto da parede lateral da
eletrônica, dentro da câmara. Eixo da passagem em Y106/Z125, atravessando
a parede em direção a -X. Removidos furo e prensa do teto. Bucha TPU única
com três canais Ø1,30 mm para fios Ø1,36 mm; montagem pelos fios antes da
conexão interna. Retenção e vedação ainda precisam de teste. A descida até
a PCB usa a região lateral; cobertura dos fios e suporte do sensor pendentes.

Tampa da eletrônica agora usa quatro pinos cônicos em alojamentos cegos,
sem parafusos, com entalhe para remoção. Ajustar retenção na impressão real.
A cobertura anterior do CO₂ foi mantida: usuário adiou sua revisão.
Arquivos atuais: output/v19/.


## Folga no canto traseiro — v0.20

Passagem lateral do sensor deslocada 16 mm para a frente: centro Y90/Z125.
A borda da bucha Ø20 termina em Y100; a parede interna traseira está em Y111.
Sensor de referência movido para X8..15/Y80..100/Z117,5..132,5, com verificação
de colisão contra a carcaça. Peça verde é a bucha TPU, não o sensor.
Arquivos atuais: output/v20/.


## Tampa única de manutenção — v0.21

A tampa traseira da eletrônica e a cobertura superior dos fios formam agora
uma única impressão removível para cima. A cabeça do sensor CO₂ e a passagem
lateral do sensor de temperatura ficam dentro dessa região seca protegida.
RJ45 e PCB permanecem na estrutura fixa; a cobertura não leva conexões.
Duas guias verticais e dois pinos superiores posicionam a tampa; retenção por
ajuste ainda exige teste. A tampa do misturador e sua junta continuam
independentes para fechar a câmara de gás.

Montagem: retirar a cobertura inteira; colocar as três porcas M4 nos canais
laterais com pinça; assentar a junta e a tampa do misturador; apertar os três
parafusos por cima. Os alojamentos sextavados seguram as porcas contra rotação.
Não é necessário segurar uma chave por baixo ao apertar. Retirar a cobertura
novamente para acessar essas ferragens em manutenção. Folgas de encaixe,
retenção das porcas e vedação precisam da impressão de teste.

O visualizador inclui “Retirar tampa de manutenção”; ao retirar a tampa do
misturador, também afasta a cobertura para mostrar o acesso.
Arquivos atuais: output/v21/.


## Alinhamento e reforço da lateral — v0.22

Base lateral e cobertura com o mesmo limite externo X-59, frente Y11 e
traseira Y128. Teto da cobertura alinhado ao teto da carcaça em Z150.
Folga nominal de 0,3 mm entre a cobertura e a carenagem fixa; espessura
lateral da cobertura 2,75 mm e teto 3 mm. Painel traseiro com nervura
interna longitudinal, conservando guias e retirada vertical.
RJ45 mantém espessura local de 1,6 mm por rebaixo interno.
Corpo nominal 190 × 141 × 160 mm. A altura da cabeça do sensor é uma
referência provisória; confirmar espaço para curva dos fios no protótipo.
Arquivos atuais: output/v22/.


## Junção sobreposta — v0.23

Borda inferior da cobertura prolongada até Z98 como saia de 1,2 mm,
encaixando em rebaixo da base. A sobreposição cobre a folga horizontal
anterior; a folga nominal de 0,3 mm passa a ficar no interior da junção.
A retirada continua vertical. Essa cobertura protege a eletrônica, mas
não substitui a vedação independente da tampa do misturador.
Arquivos atuais: output/v23/.


## Quatro pinos na tampa — v0.24

Fixação da tampa de manutenção alterada para quatro pinos cônicos
Ø3,2 × 2 mm em duas fileiras, distribuídos num retângulo de 26 × 5 mm
no apoio traseiro. Guias e borda sobreposta mantidas. São encaixes por
ajuste, sem trava elástica; resistência e retenção devem ser testadas.
Arquivos atuais: output/v24/.


## Apoio inferior e eixos das linguetas — v0.25

Quatro pinos da manutenção redistribuídos: dois no apoio superior e dois
na base do painel traseiro, encaixando em soleira integrada à carcaça.
Guias laterais e nervura traseira mantidas. Os pinos são posicionadores
por ajuste; não há garantia de retenção sem ensaio impresso.

Eixos das linguetas são parafusos M4 de referência, corrigidos para haste
30 mm (Y-23..7); porcas em Y3,2..6,7, dentro dos apoios fixos. Eixo X-9
e raio 2 mm ficam fora da câmara útil (X mínimo 4 mm). As linguetas e
knobs são impressos; parafusos e porcas não são exportados como STL.
Pedido sobre pinos impressos precisa distinguir dobradiça e fixação das
linguetas antes de trocar o mecanismo roscado.
Arquivos atuais: output/v25/.


## Fechos imprimíveis, folgas e pés — v0.26

Pinos de dobradiça Ø3 × 28 mm mantidos e agora exportados em STL.
Fechos substituídos por manípulo e haste roscada numa peça impressa,
rosca própria Ø8/passo2, com porca sextavada impressa. Não é rosca M4.
Porca entra pelo canal lateral do apoio e fica impedida de girar; inserir
porca, colocar lingueta e rosquear o manípulo pela frente. O eixo permanece
em X-9, fora da câmara útil. Testar rosca e carga de aperto antes de usar.

Aba externa da bucha do sensor de temperatura reduzida de Ø20 para Ø16,
e eixo elevado de Z125 para Z127,5. Folga nominal de 2,5 mm entre a aba
e a face superior da tampa do misturador. Referência do sensor interno
em X8..15/Y80..100/Z120..135.

Dois pés integrados de 16 × 16 mm sob a lateral, na frente e atrás,
com base no mesmo Z-10 da carcaça. Conferir estabilidade com componentes
e mangueira montados; distribuição de massa real não foi medida.

Tampa de manutenção com quatro pinos: dois superiores e dois inferiores.
Arquivos atuais: output/v26/.
# incubadora3d


## Lingueta central e sincronização do visualizador — v0.27

Um único fecho impresso em Z70 substitui os fechos inferior e superior.
O puxador foi deslocado 22 mm para a direita para liberar a lingueta central.
Mantidos dois pés integrados de 16 × 16 mm apenas sob a lateral CO₂/eletrônica,
em Y13 e Y109, com base Z-10 no mesmo plano do fundo da câmara.
O HTML anterior estava desatualizado; ambos os HTML agora são gerados juntos.

A auditoria de peças rígidas inclui a carcaça. Também verifica abertura da
porta de 0° a 110° e giro de liberação da lingueta de 0° a 90°, a cada 5°.
Compressões intencionais de TPU são excluídas da auditoria rígida; a rosca
impressa é conferida separadamente. Isso não simula deformação ou tolerâncias
reais. Um só fecho exige testar a compressão da junta no topo e na base.
Relatórios: `output/v27/clash_report.json` e `compatibilidade_k1c.json`.


## Cantos fechados, montagem impressa e passagem discreta — v0.28

Fechados os quatro canais longitudinais entre os cantos R8 da carcaça inicial
e as paredes externas de isolamento. Preservados cavidade, canal e junta TPU.
Puxador aproximado 12 mm da trava em relação à v27, com borda em X17 e
folga estática de 6 mm para a ponta da lingueta travada.

Fecho: lingueta, manípulo com haste helicoidal Ø8/passo2 e porca sextavada
são STL separados. Inserir a porca pelo canal lateral; posicionar a lingueta
e rosquear o manípulo pela frente. As superfícies helicoidais estão no CAD
e no STL; não são cilindros ilustrativos nem roscas M4 padronizadas.

Dobradiças: pinos agora têm cabeça integral, corpo liso Ø3,8 e ponta com
rosca própria Ø4/passo1; furos Ø4,4. Inserir por cima com a porta alinhada
e rosquear a porca impressa por baixo. Cabeça e porca retêm axialmente o pino.
Há folga axial nominal; não apertar a ponto de prender o movimento da porta.
A porca dos pinos inclui chanfro de entrada de 0,5 mm para iniciar o engate.
A geração das roscas foi corrigida para manter um núcleo maciço, com
checagem de volume e movimento helicoidal. Resistência, qualidade das
roscas e folgas de impressão precisam de amostras.
Os três M4 da tampa do misturador continuam sendo ferragens independentes.

Passagem entre câmaras reduzida de Ø8 para Ø4, em Y60/Z34, diretamente
na parede comum. O preenchimento em torno do furo veda a comunicação com
as células de isolamento e fica dentro da parede. Nenhum tubo saliente.
O destaque rosa fica restrito à espessura da parede, identificado como
referência, excluído do STEP e dos STL. O diâmetro é de ensaio: não foi
calculado a partir de vazão/pressão e não garante proteção contra umidade.
Validar troca de gás e condensação antes de uso; restrição não é válvula.

Verificações adicionais: quatro cantos fechados, inserção dos pinos, entrada
lateral da porca do fecho e movimento helicoidal das duas roscas. Relatórios
atuais em `output/v28/`, incluindo `clash_report.json` e `compatibilidade_k1c.json`.

Na auditoria externa, peças roscadas usam envelopes conservadores que incluem
os filetes. Os pares macho/porca usam a geometria real, com testes de
movimento e pontos internos para confirmar folga e retenção axial.

Por solicitação do usuário, os testes de movimento das tampas foram retirados
da rotina atual. Mantida a verificação de interferências na posição montada.

Atualização de escopo: todos os testes de movimento ficam desativados por
padrão. A rodada atual verifica desenho e interferências estáticas. Usar
`python cad/model.py --check-movements` somente na futura rodada de movimentos.


## Fechamento frontal dos quatro cantos — v0.29

Cada encontro da parte curva com a parte reta recebe um tampão frontal
plano de 3 mm, integrado ao corpo. Substitui o preenchimento longitudinal
da v28: o espaço de ar atrás dos cantos é mantido. O canal e a junta TPU
são preservados. Verificados material na frente e vazio atrás dos quatro
cantos. Sem testes de movimento nesta revisão. Arquivos: `output/v29/`.

## Revisão v0.30

Haste do manípulo com 24 mm lisos (Ø6,16 mm) e rosca Ø8/passo 2
apenas nos 7 mm finais, incluindo os 5 mm de encaixe na porca.

## Revisão v0.31

Haste lisa do manípulo aumentada para Ø8 mm, igual ao diâmetro externo
da rosca, com folga radial de 0,35 mm nos furos Ø8,7 mm. Rosca mantida
apenas na ponta junto à rosca integrada da base.

Eliminadas a porca separada do fecho e as três porcas da tampa CO₂,
assim como seus canais de acesso lateral. A tampa usa três parafusos
impressos Ø4/passo 1, com 6 mm roscados na ponta e haste lisa Ø4.
As roscas fêmeas fazem parte da base; eventual desgaste exige reparo
ou reimpressão da base. As porcas dos pinos da dobradiça permanecem.
