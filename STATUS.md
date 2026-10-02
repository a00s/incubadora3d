# Estado atual — v0.57

Versão atual: **v57**, gavetas em guias abertas com chanfro de entrada e lâminas em alojamentos inferiores, sem sobreposição por cima. As notas anteriores abaixo documentam o histórico.

- Arquivos atuais: `output/v57/`; revisões anteriores preservadas.
- Uma lingueta central em Z70, com haste Ø8 e rosca fêmea integrada à base.
- Puxador em X17, aproximado 12 mm do fecho em relação à v27.
- Base lateral contínua e oca até Z-10, sem pés separados; frente curva
  acompanhando o compartimento CO₂ e tampa de manutenção no mesmo perfil.
- Tampa de manutenção com um M4×12 metálico inferior traseiro diretamente em furo cego
  Ø3,5 × 9,9 mm abaixo da PCB, na região seca, sem porca; quatro pinos removidos, guias com mais folga.
- Bucha do sensor com aba Ø16 e passagem Y90/Z127,5.
- Gavetas com profundidade 72 mm e folga de 26 mm até a chapa de referência.
- Alimentação com caixa encaixada e furo Ø8; fios do aquecedor 2 × Ø1,68 mm,
  canais TPU Ø1,60 mm. Sensor: 3 fios Ø1,36 mm, canais TPU Ø1,30 mm.
- `cad/build_viewer.py` gera os dois HTML a partir da mesma malha atual.

- Quatro cantos fechados apenas na frente com tampões de 3 mm;
  cavidades de ar atrás e canal da junta TPU preservados.
- Passagem entre câmaras Ø5,6 mm, para encaixe opcional da mangueira de
  silicone Ø externo 5,8 mm; furo no mesmo local e formato.
- Dobradicas compactas com dois M4×20 escareados e porcas metalicas na porta;
  buchas PC limitam o aperto e preservam a folga de giro.
- Rosca do fecho Ø8/passo2 integrada ao apoio, sem porca nem abertura lateral.
- CO₂ fechado com teto integrado ao corpo; sem tampa, junta ou parafusos.
  Mantida somente a abertura superior do sensor e sua bucha TPU.

## Validação geométrica

Auditoria estática de peças rígidas, incluindo carcaça, continuidade das
passagens e núcleo maciço das roscas. Envelopes conservadores representam
as peças roscadas contra os demais componentes; compressão TPU excluída.
A tampa de manutenção tem remoção vertical verificada. Na v45 também foram
conferidos o envelope contínuo de inserção do inox e cinco posições da porta ampliada.
Os demais testes de movimento e caminhos de montagem foram adiados a pedido
do usuário. Executar futuramente uma única rodada com:
`python cad/model.py --check-movements`.
Relatórios: `output/v47/build.log`, `clash_report.json` e
`compatibilidade_k1c.json`. Verificação estática não garante movimento.

## Pendências físicas e de projeto

- Ensaio de vedação com fecho único, especialmente topo e base da porta.
- Testar retenção/resistência de roscas, pinos, encaixes e estabilidade lateral.
- Filamentos e dureza TPU; compressão e estanqueidade das vedações.
- Conector de alimentação real, potência do aquecedor, chapa e sua fixação.
- Altura/fios da PCB e suporte definitivo do sensor de temperatura.
- Escape/alívio, pressão, limpeza, condensação e desempenho térmico/CO₂.
- Validar passagem Ø5,6 com vazão real; o furo não garante bloqueio de umidade.
- Fatiamento, orientação e suportes antes de imprimir.

Sem validação operacional ou simulação térmica/de escoamento.

Visualizador: corte horizontal ajustável entre −10 e 150 mm, com fechamento
das superfícies seccionadas e cavidades internas preservadas.

Manípulo: haste lisa por 24 mm e rosca apenas nos 7 mm finais junto à rosca integrada.

Haste lisa Ø8 mm, com folga radial de 0,35 mm no apoio e na lingueta.

Traseira do corpo e da tampa lateral niveladas em Y125, sem ressalto.
Guias recuadas e pinos da tampa de manutenção removidos; envelope do corpo 190 × 141 × 160 mm.
Profundidade interna nominal da eletrônica: 22,5 mm.

Lingueta ampliada com aba para os dedos, três relevos de pega e chanfro
na face de contato. Sem testes de movimento nesta revisão.

## Ajuste pontual da tampa de manutenção — v36

Somente `corpo_integrado.stl` e `tampa_manutencao_CO2_eletronica.stl`
foram alterados; os outros 28 STLs são idênticos, byte a byte, à v32.
Fora dos encaixes e da fixação, corpo e tampa têm propriedades das faces
e propriedades de massa correspondentes. A traseira permanece em Y125;
a cabeça do parafuso fica dentro de um rebaixo Ø8,5 × 4,2 mm.

Retirada vertical da tampa conferida em nove alturas, sem o parafuso;
auditoria estática de 55 pares rígidos passou. Envelopes das peças cabem
na K1C com a margem prevista. Visualizador conferido no navegador.
Relatório: `output/v47/localized_change_report.json`.

Conferir fisicamente o ajuste com o novo filamento e a retenção do M4
no furo piloto; a auditoria representa a raiz da rosca e não simula
o parafuso formando rosca no plástico.

Ajuste inferior v36: centro do parafuso em Z10,5 (3,5 mm abaixo da v34);
apoio reduzido de 15 para 11,5 mm de altura. Folga local no piso da
eletrônica para receber o reforço interno, preservando a borda inferior
da tampa em Z5 e as paredes das câmaras.

Encaixe v36: duas linguetas 8 × 3,5 × 1,5 mm, ponta chanfrada de 0,4 mm,
alojamentos cegos na região seca acima da PCB. Parafuso inferior e seu
rebaixo mantidos exatamente na posição da v35.

## RJ45 e eletrônica — v37

RJ45 rebaixado: centro em Z32 mm, abertura de Z22,345 a Z41,655 mm.
Alívio interno de inserção entre Z18,5 e Z45,5 mm, acima do apoio do
parafuso inferior (topo em Z16,5 mm). PCB e suportes elevados 30 mm;
a placa ocupa Z52 a Z95,12 mm, acima do RJ45. Mantidos parafuso, tampa
e encaixes da v36. Altura real dos componentes e corpo do keystone
ainda precisam ser conferidos com as peças físicas.

Validação v37: 55 pares geométricos conferidos, sem interferências; retirada
vertical da tampa passou e STL cabem na K1C com a margem prevista.
28 STL permanecem idênticos à v36, incluindo a tampa. Visualizador
regenerado; conferência visual no Chromium indisponível porque o ambiente
não criou um contexto WebGL.

## Espaço dos conectores e sulco aberto — v38

Placa mantida em Z52–95,12 mm, com 10 mm livres abaixo (Z42–52) e acima
(Z95,12–105,12). Retirado o apoio central inferior que ocupava a região
do conector; guias laterais mantidas. A abertura no teto da caixa permite
aproveitar o espaço seco sob a tampa existente. Topo externo permanece
em Z150 mm, igual ao topo da incubadora.

A passagem fechada dos fios foi substituída por um sulco de 7 mm aberto
até a borda traseira. Retire a tampa, coloque o cabo lateralmente no sulco
sem passar o conector pelo furo e recoloque a tampa. Com a tampa montada,
o caminho dos fios tem seção livre de 7 × 7 mm; o reforço interno da tampa
foi recortado localmente para não ocupar esse caminho. A parede e a tampa
vedada do misturador permanecem preservadas.

Os envelopes de conferência dos conectores usam a largura da placa e
10 mm de profundidade a partir da face traseira da placa. A profundidade
real dos conectores e das curvas dos fios da montagem fotografada ainda
precisa de medida; a foto não fornece escala suficiente para verificá-la.

Para liberar a margem superior, há um recorte somente na aba externa seca
do misturador, fora da câmara e do canal de vedação. O parafuso CO₂ traseiro
foi deslocado 2 mm em X, para manter parede ao redor da rosca.

Validação v38: 55 pares rígidos sem interferências, folgas dos conectores
e caminho dos fios livres, retirada vertical da tampa verificada. STL
conferidos para K1C; visualizador regenerado. PCB e M4 de manutenção
permanecem idênticos à v37. Renderização no navegador não repetida nesta
versão devido à indisponibilidade de WebGL constatada no ambiente.

## Fechamento do CO₂ e passagem retangular — v39

Teto do misturador integrado ao corpo: sem tampa removível, junta do teto,
parafusos, arruelas ou roscas do CO₂. A abertura do sensor Ø20,4 mm e sua
bucha TPU foram mantidas; a conexão inferior de gás e a comunicação
interna com a câmara continuam existentes.

Sulco aberto da eletrônica eliminado. O teto seco foi fechado acima da
margem dos conectores, com uma única passagem retangular de 15 × 10 mm
junto à placa, acessível removendo a tampa de manutenção. A placa continua
em Z52–95,12 mm, com pelo menos 10 mm livres em cada ponta. O novo teto
seco tem a face inferior em Z108 mm; a altura externa continua em Z150.
A passagem fica totalmente contornada por material, sem abertura até a borda.

Planejamento de orientação, fatiamento e impressão sem suportes internos
adiado conforme pedido; esta revisão não comprova impressão sem suportes.

Validação v39: auditoria estática de 34 pares rígidos passou, corpo
único válido, passagem retangular livre e retirada da tampa de manutenção
conferida. PCB, sensor, bucha e M4 de manutenção idênticos à v38.
STL conferidos para K1C, visualizador regenerado; renderização WebGL
não repetida devido à limitação já constatada no ambiente.

## Entrada externa CO₂ e amostra — v40

Entrada antiga inferior, com curva de 90° e canal Ø2,6 mm, removida.
Novo alojamento lateral externo para mangueira de silicone Ø externo
5,8 mm: encaixe Ø5,6 mm com 12 mm de profundidade e chanfro de entrada
até Ø6,2 mm. Mangueira entra no alojamento e apoia no degrau interno.
Canal reto Ø3,5 mm segue até o misturador, sem curva nem trecho cego.
Centro da entrada em Y60/Z18; eixo para fora em −X. Projeção externa
12 mm, diâmetro externo do alojamento 10 mm; reforço contínuo liga a
parede externa ao misturador, isolando o gás das cavidades de ar.

Amostra: `output/v47/amostra_entrada_CO2_mangueira_OD5p8.stl`.
Ela reproduz o alojamento, profundidade, chanfro, degrau e canal do corpo.
Teste o aperto da mangueira e a passagem de ar antes de imprimir o corpo.
A interferência nominal de 0,2 mm precisa de ensaio com o filamento e a
mangueira reais; a geometria livre não garante que o fatiamento deixe o
canal aberto. Orientação e suportes do corpo ainda serão definidos.

Validação v40: 34 pares rígidos sem interferências; canal reto e alojamento
conferidos livres; amostra separada com canal horizontal livre. Somente
o STL do corpo foi alterado; os outros 23 STL mantidos são idênticos à v39.
Envelopes conferidos na K1C; visualizador atualizado. Renderização no
navegador não repetida por limitação de WebGL anteriormente constatada.

## Entrada traseira, base contínua e frente curva — v41

Entrada do CO₂ voltada para trás (+Y), em X−23/Z10,5, na altura do M4
mas 11,5 mm ao lado dele. Ponta em Y137, 12 mm além da traseira Y125.
Alojamento Ø5,6 × 12 mm para mangueira Ø externo 5,8 mm, chanfro Ø6,2
e canal reto Ø3,5 mm mantidos. O tubo atravessa a região inferior da
caixa seca com paredes próprias até chegar ao misturador. A tampa tem
um recorte inferior aberto de 10,8 mm para levantar sem retirar o tubo.

Os dois pés foram retirados. A estrutura lateral agora chega continuamente
a Z−10, com cavidades e piso de 2,5 mm, no plano de apoio da incubadora.
A frente quadrada foi substituída por um arco de raio 49 mm, centrado
em X−10/Y60, acompanhando o CO₂; a extensão traseira da eletrônica foi
mantida. Tampa, saia e alojamento seguem o mesmo perfil curvo.
PCB, margem de 10 mm dos conectores, RJ45 e teto integrado CO₂ mantidos.

A amostra separada da entrada continua disponível em
`output/v47/amostra_entrada_CO2_mangueira_OD5p8.stl`, atualizada para o
comprimento do canal traseiro. Planejamento de orientação e suportes
permanece pendente conforme a etapa combinada.

A parede curva externa tem 2,5 mm, com uma faixa mais espessa entre
Z97,5 e Z102 sob o encaixe da tampa. O piso da base permanece em 2,5 mm.

Validação v41: 34 pares rígidos sem interferências; base contínua, canal
traseiro e retirada vertical da tampa conferidos. 22 STL idênticos à v40;
alterados somente corpo, tampa e amostra da entrada. Envelopes conferidos
para K1C; visualizador atualizado. Volume sólido do corpo + tampa
reduzido 2.56% frente à v40; consumo de filamento depende do fatiamento.
Renderização no navegador não repetida por limitação de WebGL conhecida.

## Parede única CO₂ e traseira plana — v42

A parede interna semicircular duplicada foi retirada. A parede curva
externa passa a fechar o compartimento de CO₂, com 4 mm nominais de
espessura e faixa reforçada junto ao encaixe da tampa. O espaço do gás
foi ampliado; a parede traseira o separa da eletrônica. Piso do gás em
Z−6, base em Z−10; teto integrado e abertura do sensor mantidos. A tampa
de manutenção permanece separada sobre a região seca superior.

A entrada termina em Y125, no mesmo plano da traseira do corpo, sem
projeção. Alojamento Ø5,6 × 12 mm para mangueira Ø externo 5,8 mm e canal
reto Ø3,5 mm; transição cônica de 2 mm substitui o degrau interno.

STL do corpo com traseira apoiada na mesa:
`output/v47/impressao_traseira_na_mesa/corpo_integrado.stl`.
Rotação −90° em X; direção de construção corresponde a −Y do CAD.
A amostra da entrada foi orientada com a boca na mesa, reproduzindo
essa direção de construção. O corpo fica com envelope 190 × 160 × 141 mm
nessa orientação. Os demais arquivos da K1C conservam a orientação CAD.

O bocal rente elimina o ressalto que afastaria a traseira da mesa; a
transição interna foi adaptada para diminuir balanços. Suportes, pontes,
roscas, canais da junta e demais detalhes exigem revisão no fatiador;
ainda não há validação de impressão inteiramente sem suportes.

Validação v42: 34 pares rígidos sem interferências; ausência da antiga
parede interna conferida, canal livre e traseira em Y125. STL orientado
com Z mínimo zero e envelope nominal 190 × 160 × 141 mm, dentro da K1C
com margem. Dimensões STL conferidas com tolerância de 0,01 mm.
Volume sólido do corpo + tampa reduzido 3.60% frente à v41.
Visualizador regenerado; conferência WebGL não repetida no ambiente.

## Fechamento interno para impressão traseira em PC — v43

Contorno externo curvo mantido. O fechamento curvo interno do CO₂ foi
substituído por uma face inclinada de 45° na direção de construção −Y.
A cavidade principal segue a linha Y = −X + 5, de X−55/Y60 a X−10/Y15.
A margem junto ao encaixe e o pescoço superior recebem o mesmo perfil
com seus respectivos raios. Para uma camada de altura h, o avanço
nominal nessa face é h. Isso limita o balanço geométrico dessa região;
a impressão real de PC a 45° ainda exige teste com o filamento utilizado.

A face acrescenta material na frente e reduz o volume interno do gás,
sem uma parede separada ou suporte descartável dentro da câmara.
Sensor, passagem de gás, entrada traseira embutida, placa e tampa de
manutenção mantidos. Essa revisão trata do fechamento do CO₂; não é
uma garantia de ausência de suportes nos demais detalhes do corpo.

Amostra específica do fechamento, já na direção de impressão traseira:
`output/v47/amostra_fechamento_CO2_45graus_PC.stl`.
Ela reproduz uma fatia de 8 mm da parede externa e do fechamento interno
em escala real, com a parede compartilhada representada. Teste a face
inclinada em PC, sem suportes, antes de imprimir o corpo completo.
O STL do corpo orientado continua na pasta `impressao_traseira_na_mesa`.

Material informado pela imagem: CC3D PC laranja 1,75 mm. Formulação,
ficha técnica, temperaturas e classificação de chama ainda não confirmadas;
nenhum perfil térmico ou de velocidade foi presumido. Referências consultadas: documentação oficial
Prusa sobre PC (https://help.prusa3d.com/article/polycarbonate-pc_165812)
e pontes (https://help.prusa3d.com/article/poor-bridging_1802), além da
compatibilidade oficial K1C (https://www.creality.com/products/k1c-carbon-3d-printer).

O usuário pretende usar PC para reduzir o risco de incêndio. O anúncio
mostrado não apresenta classificação de retardância à chama. A resistência
ao fogo desta formulação e da peça impressa não foi verificada; não há
alegação de material antichama ou de proteção contra incêndio no projeto.
Referência: https://www.ul.com/services/ul-blue-card-plastics-additive-manufacturing
(as classificações dependem também do processo de impressão).

Validação v43: 34 pares rígidos sem interferências; amostra do fechamento
conferida por normais STL: faces descendentes fora da base limitadas a 45°.
Tampa, placa, sensor, bucha e M4 idênticos à v42. Volume sólido de corpo
+ tampa aumentou 6.35% por causa do preenchimento interno.
Arquivos conferidos para K1C; visualizador regenerado. Teste físico em
PC, revisão integral no fatiador e segurança contra incêndio não validados.

## Passagem interna para mangueira opcional — v44

Passagem entre compartimento CO₂ e câmara ampliada de Ø4 para Ø5,6 mm.
Mesma posição Y60/Z34, mesmo eixo X, formato circular e parede atravessada
(14 mm). O tubo é opcional e não foi acrescentado à montagem. O diâmetro
repete o encaixe da entrada para mangueira de silicone Ø externo 5,8 mm,
com interferência nominal de 0,2 mm. O reforço maciço Ø12 mm ao redor da
passagem foi mantido, isolando o canal das cavidades de isolamento.

Amostra do furo: `output/v47/amostra_passagem_interna_CO2_OD5p8.stl`.
Reproduz os 14 mm de caminho e Ø5,6 mm, com furo horizontal para testar
a impressão e o ajuste da mangueira. Demais dimensões e componentes
mantidos. Ajuste final depende de filamento, fatiamento e mangueira reais.

Validação v44: 34 pares rígidos sem interferências; passagem e amostra
conferidas livres. Somente o STL do corpo mudou; 25 STL idênticos à v43.
Envelopes conferidos para K1C, visualizador regenerado.

## Câmara livre para revestimento inox inserido pela frente — v45

Cavidade e abertura frontal com a mesma seção de 112 × 132 mm, raio 6 mm
nos quatro cantos vistos de frente, constante até Y111. Fundo plano:
as uniões das paredes, teto e piso com o fundo não têm arredondamento.
Os apoios e batentes antes integrados às paredes foram removidos.
`suporte_gavetas_removivel.stl` reúne trilhos nas alturas originais,
quatro montantes e travessas traseiras; pés ajustados ao raio inferior.
Apoia no fundo do revestimento,
sem depender da chapa fina para sustentar as gavetas. Bandejas mantidas.

O canal da junta foi deslocado 4 mm para fora, mantendo seu perfil de
retenção. A borda de vedação da porta passa a 128 × 148 mm; o isolamento
celular central foi preservado. Eixo das dobradiças movido de X126 para
X130; eixo do fecho de X−9 para X−13 para liberar a borda ampliada. A borda externa do quadro cresce por uma rampa de 45° em impressão
traseira. Corpo com envelope 195 × 141 × 160 mm; traseira permanece Y125.

Material informado na imagem: EFUTURETIME inox 304, 0,05 × 150 × 1000 mm.
O modelo da caixa metálica tem dimensões externas 111 × 131 × 110 mm,
raio externo 5,5 mm e espessura nominal de 0,05 mm. Folga lateral, superior
e inferior nominal de 0,5 mm; folga traseira de 1 mm. A chapa é um
revestimento fino; o suporte das bandejas é uma peça independente.

`revestimento_inox_referencia.step` contém a caixa aberta na frente,
com furos alinhados às passagens existentes: CO₂ Ø5,8 mm e passagens de
cabos Ø14 mm, para liberar as abas internas TPU. O encaixe Ø5,6 mm do
silicone permanece na parede plástica; não foi ampliado.
Montar revestimento antes das buchas de cabos, aquecedor e sensor interno.
As folgas e a fabricação em chapa ainda precisam de teste físico.

`molde_caixa_inox_referencia.step` e `.stl` fornecem o volume interno
nominal da caixa, 110,9 × 130,9 × 109,95 mm, raio 5,45 mm. O STL está com
o fundo na mesa. É referência geométrica para conformação; não é uma
planificação de corte com compensações de dobra ou emendas. O SVG
`perfil_caixa_inox_1para1.svg` mostra a seção externa em escala 1:1;
imprimir a 100%, sem ajustar à página, e conferir a barra de 50 mm.

Validação v45: 54 pares rígidos sem interferências.
Envelope contínuo de inserção frontal livre; porta conferida a 0°, 30°,
60°, 90° e 110°, com entrada do inox livre a 110°. Apoios sem colisões
com inox, bandejas e corpo. 18 STL idênticos à v44; alterações
da porta, junta, dobradiças e fecho acompanham a abertura ampliada.
STL para K1C conferidos com margem de 5 mm; corpo traseira na mesa
195 × 160 × 141 mm. Visualizador regenerado; renderização WebGL não
verificada neste ambiente. Encaixe físico, conformação do inox e revisão
integral de suportes no fatiador continuam pendentes.

## Formato de entrega para o usuário

O usuário utiliza Creality Print com K1C. Entregar peças e amostras de
impressão em STL, com links diretos; STEP permanece como fonte CAD auxiliar.
O molde já tem STL em `output/v47/molde_caixa_inox_referencia.stl`,
com fundo na mesa. Para o corpo, usar o STL específico em
`output/v47/impressao_traseira_na_mesa/corpo_integrado.stl`.
A pasta `k1c_posicionados` centraliza peças, mas não define a orientação
final de todas elas nem contém projeto fatiado com perfil de PC validado.

## Dobradicas metalicas, labio flexivel e projeto Creality Print — v46

Kit confirmado pela imagem: M4 × 4/6/8/10/12/16/20 mm, com porcas M4.
Cabeca escareada confirmada pelo usuario; TPU da junta: 95A.
As duas dobradicas usam M4 × 20 escareados, com porcas metalicas em
alojamentos hexagonais antirotacao na porta. Os pinos e porcas impressos
foram removidos. A pilha foi compactada para 17,5 mm. Cada dobradica tem
uma bucha PC Ø6 externo / Ø4,4 interno × 8,5 mm; ela limita a compressao
entre os olhais da porta, com 0,25 mm de folga em cada lado do olhal fixo.
Furo do olhal fixo Ø6,4 mm. Porca nominal 7 mm entre faces e 3,2 mm de
altura; alojamento 7,3 mm entre faces × 3,4 mm. Assento escareado 90°,
Ø8,8 mm / Ø4,4 mm × 2,2 mm. Apertar suavemente e confirmar giro livre
na amostra antes da impressao completa. As dimensoes reais da ferragem
e a retracao da impressao ainda precisam de teste.

Eixo das dobradicas em X130/Y−6. O topo frontal dos olhais moveis termina
no plano Y−1, junto da face interna da porta, para apoiar essa face na mesa.
A borda do apoio do fecho recuou 0,25 mm, liberando o inicio da abertura.
Corpo com envelope 195 × 141 × 160 mm; traseira Y125 mantida.

A junta conserva o pe de retencao e o canal. A parte de contato passa a
dois labios inclinados, com espessura radial de 0,6 mm e alcance livre
2,5 mm a partir da frente do corpo. A face fechada da porta fica a 1 mm,
com deflexao nominal de 1,5 mm. Ha duas linhas de contato, com espaco
entre os labios para flexionar. A compressao nao foi simulada por elementos
finitos; o CAD mostra a forma livre e exclui a deformacao TPU da auditoria
rigida. O fecho central existente continua regulando o aperto.

O `anel_centragem_porta.stl` e uma peca separada de 108,8 × 128,8 × 4 mm,
com canto R4,4 e chanfro de entrada de 0,6 mm. Entra 3 mm na camara,
com folga nominal de 1,05 mm para o inox. Fixacao por quatro M4 × 8
escareados nos pontos X11/X109 e Z30/Z110. Os pilotos Ø3,5 × 4,2 mm
na porta sao cegos e preservam pelo menos 0,8 mm ate a face externa do
painel de vedacao. O anel alinha a porta; a vedacao primaria continua
na junta TPU do corpo. Ele e impresso separado, com a face traseira na
mesa, e depois montado, preservando a face plana de impressao da porta.

Amostras:
- `amostra_dobradica_base_M4x20.stl` e `amostra_dobradica_porta_M4x20.stl`:
  uma dobradica completa em miniatura, usar uma bucha e um M4 × 20 com porca.
- `amostra_junta_TPU.stl`: trecho real de 35 mm, labios 0,6 mm.
- `amostra_junta_TPU_labios_0p8.stl`: alternativa 0,8 mm para comparar
  flexibilidade e formacao das paredes pelo fatiador.
- `amostra_canal_rigido.stl` e `amostra_pressao_junta.stl`: canal e placa
  com batentes reproduzindo o vao fechado de 1 mm. Ensaio manual de
  retencao e compressao; os extremos abertos nao constituem ensaio de estanqueidade.

Nao foi identificada a origem do vazamento da impressao anterior; nao ha
alegacao de estanqueidade comprovada. Conferir contato ao longo dos quatro
lados e cantos na montagem real e depois testar vazamento. A escolha final
entre os labios de 0,6 e 0,8 mm depende dos ensaios com o TPU 95A do usuario.
Referencia geral consultada: https://eu-wholesale.polymaker.com/it/products/polyflex-tpu95
(a dureza Shore indica apenas parte da flexibilidade da peca impressa;
nao se presume que o filamento do usuario seja dessa marca).

## Projeto com bandejas para Creality Print 7.2.1

`incubadora_v46_CrealityPrint_7.2.1.3mf` agrupa todas as pecas imprimiveis,
molde e amostras, uma por bandeja, nomeadas e identificadas como PC ou TPU.
As ferragens metalicas e o revestimento inox de referencia ficam fora das
bandejas. O corpo usa o STL com a traseira na mesa; a porta usa a face de
vedacao na mesa; o anel interno usa a face traseira na mesa; junta TPU plana.
As demais orientacoes sao iniciais e precisam de revisao no fatiador.
Abrir como projeto para preservar as bandejas; importacao so de geometria
pode descartar essa organizacao. Selecionar os perfis de filamento e
processo reais e conferir as previas de camadas antes de imprimir.

O projeto identifica K1C com bico inicial de 0,4 mm; confirmar o bico
instalado. A organizacao nao inclui G-code nem temperaturas, velocidades
ou configuracoes de suporte validadas. Perfis genericos PC/TPU identificam
os materiais; trocar pelos perfis usados pelo usuario. Peças nao foram
fatiadas. A geracao e a auditoria ficam em `cad/build_creality_project.py`
e `cad/check_creality_project.py`, com `--version v46`.

O formato de malhas, metadados, referencias de bandeja e grade seguem o
codigo oficial da versao: https://github.com/CrealityOfficial/CrealityPrint/blob/v7.2.1/src/libslic3r/Format/bbs_3mf.cpp
e https://github.com/CrealityOfficial/CrealityPrint/blob/v7.2.1/src/slic3r/GUI/PartPlate.cpp .
Relatorios: `bandejas_creality.json` e `projeto_creality_verificacao.json`.

Validacao v46: 58 pares rigidos sem interferencias. Porta e anel interno
conferidos a 0°, 0,5°, 1°, 2°, 5°, 15°, 30°, 60°, 90° e 110°; anel
sem colisao com o inox durante a abertura. Canal e pe da junta conferidos.
21 STL identicos a v45. Dimensoes conferidas para K1C com margem
de 5 mm. Projeto 3MF com 32 bandejas, escala 1:1, referencias e indices
conferidos; volumes das malhas preservados em relacao aos STL de origem.
Faces degeneradas com vertices identicos provenientes da quantizacao STL
foram removidas, sem alterar o volume. Sem G-code ou fatiamento.
Visualizador regenerado. Leitura nativa pela AppImage oficial Creality
Print 7.2.1.5476 concluida com sucesso (CLI --info, saida 0): 32 objetos,
32 bandejas e 32 malhas manifold. Renderizacao na interface grafica nao
foi conferida; nao houve fatiamento.
Estanqueidade, ajuste das ferragens, compressao TPU e suportes exigem
ensaio fisico/revisao no fatiador.

## Porta em formato de escotilha — v47

A face externa da porta permanece maior e comprime a junta TPU encaixada
no corpo. A parte interna agora e um painel menor, fechado, com
108,8 × 128,8 mm e cantos R4,4. Ele entra 3 mm na abertura da incubadora,
com folga nominal de 1,05 mm para o inox. O painel e PC rigido, sem junta
TPU adicional na porta. Sua funcao e compor o ressalto da escotilha;
a vedacao permanece no contato dos labios TPU com a face externa maior.

O painel menor trava na porta por duas linguetas flexiveis, sem parafusos,
porcas ou os quatro apoios circulares da v46. Quatro pequenos apoios
retangulares na face posterior guiam a montagem no alojamento cego.
Linguetas: 20 mm livres, parede radial 1,2 mm, deflexao de entrada
nominal 0,3 mm. Os recortes de flexao ficam apenas no painel interno;
a face externa de vedacao continua fechada, com 2,6 mm de material
no fundo do alojamento cego. A retencao e a flexibilidade das linguetas
em PC precisam de teste fisico; nao foram simuladas.

A separacao em duas pecas encaixadas conserva a face plana para imprimir
a porta. O painel menor e impresso com a face voltada para a camara na
mesa, inclusive as linguetas, sem partes flutuantes. Conferir as previas
de camadas e o ajuste antes da impressao completa. As dobradicas continuam
com os M4 × 20 escareados e porcas metalicas solicitados anteriormente;
esta revisao elimina apenas os parafusos extras do painel interno.

Arquivos atuais: `output/v47/`; projeto completo em
`output/incubadora_CrealityPrint_7.2.1.3mf`. O projeto inclui todas as
pecas, molde e amostras em bandejas separadas.

Validacao v47: 59 pares rigidos sem colisao; porta e ressalto conferidos
a 0°, 0,5°, 1°, 2°, 5°, 15°, 30°, 60°, 90° e 110°, com passagem livre
da caixa inox pela frente a 110°. Leitura nativa do 3MF no Creality Print
7.2.1.5476, CLI --info: saida 0, 32 objetos e 32 bandejas; 32 malhas
manifold. Interface grafica e fatiamento nao conferidos.
30 STLs identicos a v46; so a porta e o painel interno foram alterados.
Encaixe das linguetas em PC e estanqueidade ainda exigem teste fisico.


## Porta monolítica com vedação em U — v48

Porta rígida em uma peça: painel interno integrado, sem painel removível, linguetas de união, alojamento cego ou parafusos extras. Canal perimetral em U rebaixado na face interna recebe uma borda contínua integrada ao corpo. Junta `junta_U_porta_TPU.stl` com pé alargado retido no canal e dois lábios de 0,6 mm, um de cada lado da borda. A junta externa `junta_porta.stl` do corpo foi preservada como segunda linha de vedação.

Canal: profundidade 2,9 mm; boca 2,2 mm; centro a 3,4 mm do contorno nominal. Borda rígida: largura 1 mm, projeção frontal 2,5 mm e chanfro de entrada de 0,3 mm. Folga rígida lateral nominal: 0,6 mm por lado na boca. TPU exibido em forma livre; deformação, retenção e estanqueidade precisam de ensaio físico.

Câmara rígida preservada: largura 112 × altura 132 × profundidade 111 mm, cantos R6. Revestimento inox 304: dimensões externas 111 × 131 × 110 mm, R5,5 e espessura 0,05 mm. Medidas internas do revestimento: 110,9 × 130,9 × 109,95 mm. O molde é referência de conformação, sem planificação nem compensação de dobras. Alterar a espessura exige revisar o molde.

Orientação da porta e planejamento de suportes adiados por solicitação do usuário. Orientações no projeto 3MF são apenas iniciais; não constituem validação para impressão. Arquivos atuais em `output/v48/`.

Validação v48: 57 pares rígidos com envelopes sobrepostos conferidos, sem colisões. Movimento da porta em 0°, 0,5°, 1°, 2°, 5°, 15°, 30°, 60°, 90° e 110°; entrada do inox livre a 110°. STLs dimensionados para K1C com margem de 5 mm. Projeto 3MF com 35 bandejas, estrutura, escala e índices conferidos; leitura nativa no Creality Print 7.2.1 via CLI --info com saída 0. Sem fatiamento ou G-code. Amostras de 35 mm: `amostra_U_porta_rigida.stl`, `amostra_U_porta_TPU.stl` e `amostra_U_borda_corpo.stl`; permitem ensaio manual de encaixe, sem comprovar estanqueidade nos cantos.

Visualizador v48 conferido no Chromium: junta TPU do U presente, painel separado ausente e sem erros JavaScript. Corte esquemático em `corte_vedacao_U.svg`. Apenas corpo e porta mudaram entre os STLs preexistentes; a junta do U e três amostras foram acrescentadas.


## Ressalto inteiro em V com fundo plano — v49

A alteração se aplica a todo o ressalto interno da porta, não só a um canal estreito. A peça rígida é única: base larga e ponta menor, com laterais inclinadas e cantos contínuos. O corpo recebe um assento perimetral inclinado, mais largo na boca, integrado ao quadro frontal. O fecho mantém a carga axial; a cunha comprime os lábios TPU lateralmente. Não há validação de autotravamento nem simulação de contato/deformação.

Inclinação do ressalto: avanço radial de 0,5 mm por mm axial, 26,565° em relação ao eixo de fechamento. Base do ressalto em Y−4,6 com inset 2,65 mm; ponta em Y3 com inset 6,45 mm. Dimensões X/Z: base 114,7 × 134,7 mm; ponta 107,1 × 127,1 mm. Cantos seguem o centro dos raios da câmara e do inox, em X/Z10. Assento do corpo: boca em Y−3,7 e inset 2,47375 mm, convergindo até inset 4 em Y0. Espessura radial nominal 1 mm. A abertura no plano Y0 permanece 112 × 132 mm. Geometria de ponta/ângulo da porta e assento são diferentes para manter folga rígida e espaço de deformação do TPU.

`junta_V_porta_TPU.stl` envolve o ressalto inclinado; pé retido numa ranhura com seção alargada, dois lábios anulares axiais de 0,6 mm. A junta do corpo continua com dois lábios, mas o lábio originalmente voltado para dentro foi redirecionado para fora, para liberar o assento em V. As peças TPU são exibidas em forma livre; interseções intencionais com as superfícies de vedação não representam colisões rígidas. Não se presume estanqueidade, esforço de aperto ou vida útil sem ensaio físico.

Inox comprado: 0,3 mm. Caixa metálica externa preservada em largura 111 × altura 131 × profundidade 110 mm, R5,5. Espaço interno e molde: 110,4 × 130,4 × 109,7 mm, R5,2. Suporte das bandejas reduzido para largura 109,8 mm, com folga lateral de 0,3 mm por lado; pés elevados para a face interna do inox em Z4,8. O molde antigo de 0,05 mm não deve ser usado para esta chapa. A planificação de corte e as compensações das dobras não estão incluídas.

Amostras de 35 mm: `amostra_V_porta_rigida.stl`, `amostra_V_porta_TPU.stl` e `amostra_V_assento_corpo.stl`. Testam encaixe e compressão numa lateral; extremos abertos e ausência de cantos impedem comprovação de estanqueidade da caixa completa.

Orientação de impressão da porta e suportes permanecem adiados por solicitação do usuário. O projeto 3MF traz orientações iniciais, sem fatiamento nem G-code. Arquivos atuais em `output/v49/`; corte da lateral inclinada em `corte_vedacao_V.svg`.

Referência do sensor de temperatura/umidade deslocada 0,3 mm para baixo (Z119,7–134,7), liberando o canto superior do inox de 0,3 mm. A fixação real do módulo permanece dependente das dimensões físicas.

Validação v49: 57 pares rígidos com envelopes sobrepostos, sem colisões; porta e inox conferidos em 20 posições entre 0° e 110°, incluindo 7°, 10°, 12°, 18° e 20°. Entrada do inox livre a 110°. Todos os STL cabem na K1C com margem de 5 mm. Projeto 3MF com 35 bandejas, escala e índices conferidos; leitura nativa no Creality Print 7.2.1 CLI --info com saída 0 e 35 malhas manifold. Visualizador conferido no Chromium, sem erros JavaScript, WebGL com conteúdo e controles de fecho/porta/bandejas funcionando. Sem fatiamento ou G-code; retenção e estanqueidade exigem ensaio físico.


## Caixinha traseira ampliada e parafusada — v50

Dimensões externas: largura 70 × altura 60 × profundidade 21 mm, centrada em X60/Z116 e apoiada no plano traseiro Y125. Extremos X25–95, Z86–146, Y125–146. Profundidade preservada. Envelope interno máximo 65 × 55 × 18,5 mm; duas torres de fixação ocupam os cantos diagonais. O espaço efetivo depende do conector e da sobra de fio reais. Abertura do conector Ø8, no lado −X (direita vista de trás), mantida em Y135,5/Z116.

Os dois pinos e seus encaixes de interferência foram removidos. Dois M4 × 12 metálicos prendem a caixinha, sem porcas, em pilotos cegos Ø3,5 × 9,8 mm no corpo. Centros X32/Z93 e X88/Z139. Cada piloto é cercado por um apoio sólido Ø11, de Y114,5 a Y125, preenchendo a região local de isolamento. Fundo do piloto em Y115,2; ponta nominal do parafuso em Y116. A parede quente traseira permanece de Y111 a Y115, sem corte pelos novos furos. Há 4,2 mm entre o fundo dos pilotos e a face interna plana da câmara. A geometria não substitui ensaio físico de vazamento nem validação da impressão.

A caixinha possui passagens Ø4,4 e plataformas de apoio com 3 mm. A cabeça fica em Y128, acessível por dois canais Ø9 na face traseira; referência de cabeça Ø7 × 4 mm. Confirmar medidas da cabeça real e alcance da ferramenta. Rosca metálica entra diretamente no plástico, com 9 mm de engate nominal. A passagem TPU dos dois fios do aquecedor é preservada e continua sendo a barreira de gás dessa passagem. A caixinha é externa à câmara; seus acessos de parafuso não são furos passantes na parede quente.

Montagem: encaminhar os fios na caixinha e posicioná-la sobre a passagem TPU, alinhar os dois furos e apertar os M4 pela traseira. Para retirar, remover os parafusos e puxar em +Y. Não há travas rígidas ou pinos pressionados nos alojamentos antigos. Testar a fixação com o plástico e os parafusos reais antes da impressão completa.

`amostra_caixinha_fixacao_M4.stl` contém dois componentes separados, lado a lado: um canto real da caixinha com torre, passagem e acesso de cabeça, e uma base com o piloto cego e os mesmos 4,2 mm até a face interna. Os dois componentes ocupam uma bandeja do projeto, para manter o conjunto dentro das 36 bandejas do Creality Print. Não são um ensaio de estanqueidade da caixa completa.

Arquivos atuais em `output/v50/`. Caixinha e amostra recebem orientação inicial com face traseira na mesa; a orientação e os suportes da porta permanecem adiados. Não há fatiamento nem G-code. A porta em V, seu TPU, o molde inox 0,3 mm, bandejas e demais mecanismos permanecem os da v49.

Validação v50: 60 pares rígidos com envelopes sobrepostos conferidos, sem colisões; caixinha removível em deslocamentos de 0 a 25 mm. Material da parede quente traseira preservado pelos novos pilotos, passo de fios TPU e abertura do conector livres. Porta em 20 posições entre 0° e 110° e entrada do inox continuam conferidas. Todos os STLs cabem na K1C com margem de 5 mm. Projeto 3MF com 36 bandejas, escala e índices conferidos; leitura nativa no Creality Print 7.2.1 CLI --info com saída 0, 36 malhas manifold, sem fatiamento ou G-code. Amostra de fixação contém dois componentes fechados na mesma bandeja. Encaixe das ferragens, resistência no PC e estanqueidade precisam de ensaio físico.


## Bordas retas na interface da caixinha — v51

Removido o arredondamento externo das duas arestas horizontais da caixinha no plano Y125, lado que encosta na incubadora. Topo em Z146 e base em Z86 chegam retos a essa interface, ao longo de toda a largura X25–95. As duas arestas correspondentes da face traseira exposta, Y146, continuam com raio 4 mm.

Dimensões 70 × 60 × 21 mm, espaço interno máximo 65 × 55 × 18,5 mm, dois M4 × 12 com pilotos cegos e passagem TPU dos fios preservados. Os novos furos permanecem fora da parede quente da câmara. Não há alteração da porta em V ou do molde para inox de 0,3 mm. A amostra de fixação acompanha a nova borda reta. Orientações continuam iniciais, sem fatiamento nem G-code; ajuste físico e estanqueidade exigem ensaio.


## Bordas retas, lingueta livre e pilotos curtos reforçados — v53

Mantida a caixinha 70 × 60 × 21 mm, com topo e base retos no lado Y125 que encosta na incubadora; somente as arestas da face traseira exposta recebem raio 4 mm.

A lingueta e a pega central passam de 20 para 16 mm de altura, com nervuras nos deslocamentos Z−5, Z0 e Z+5. O contato continua largo em X, com chanfro de entrada e furo de guia existentes. Ao afrouxar 0,8 mm e girar 90° para baixo, a extremidade direita fica em X−5, deixando 1 mm nominal em relação à borda da porta em X−4. O movimento de abertura com a lingueta nessa posição e sua própria rotação de liberação passam a ser conferidos sempre, mesmo sem --check-movements; não se depende da posição de 180° para liberar a porta.

Os dois M4 × 12 da caixinha são mantidos, mas entram somente 4 mm no corpo. Plataformas da caixinha com 8 mm, cabeça em Y133; ponta nominal do parafuso em Y121. Pilotos cegos Ø3,5 × 4,4 mm, fundo em Y120,6. Cada apoio é sólido Ø16 × 10 mm, entre Y115 e Y125, substituindo o espaço de isolamento local por PC contínuo. Material mínimo do apoio atrás do piloto: 5,6 mm; ao redor do piloto: 6,25 mm radiais. Total até o plano interno Y111: 9,6 mm de PC nominal, incluindo os 4 mm da parede quente original. Os novos furos não atravessam a região reforçada nem chegam a uma cavidade de ar. A traseira do corpo permanece plana em Y125; não foram adicionados ressaltos externos que impedissem o apoio de impressão traseiro.

A passagem TPU dos fios permanece; a caixinha é externa à câmara e não substitui sua barreira de gás. Resistência do engate curto no PC, limite de aperto e estanqueidade precisam de ensaio físico; o desenho não comprova vazamento zero. `amostra_caixinha_fixacao_M4.stl` contém o canto com plataforma de 8 mm e a base com o novo piloto cego, em dois componentes separados na mesma bandeja. Verificar retenção manual dos dois M4 sem forçar o aperto antes de imprimir o corpo inteiro.

Peças rígidas alteradas desde v50: corpo, caixinha e lingueta. Porta em V, molde e revestimento inox de 0,3 mm e bandejas permanecem iguais. Arquivos atuais: `output/v53/`; projeto Creality Print e visualizador principais atualizados. Sem fatiamento ou G-code; orientação e suportes da porta permanecem adiados.

Validação v53: 60 pares rígidos com envelopes sobrepostos sem colisões. Lingueta liberada a 90° conferida com porta em 21 posições de 0° a 110°, incluindo 0,1°, 0,25° e 0,5°; rotação de liberação da lingueta em 19 posições de 0° a 90°. Material da parede quente preservado pelos pilotos; piso sólido de 5,6 mm e material radial de 6,25 mm ao redor dos pilotos conferidos por volumes testemunha. Caixinha removível nos deslocamentos 0–25 mm. Todos os STL cabem na K1C com margem de 5 mm. Projeto 3MF com 36 bandejas, escala e índices conferidos; CLI nativa Creality Print 7.2.1 com saída 0 e 36 malhas manifold. Visualizador no Chromium sem erros JavaScript, WebGL com conteúdo e controles de fecho/porta/bandejas funcionando. Sem fatiamento ou G-code. Ensaios físicos de retenção e estanqueidade pendentes.


## Cavidades para carcaça impressa com a traseira na mesa — v54

A carcaça constrói de Y125 para −Y. A grade de 396 pequenas cavidades foi
substituída por 23 cavidades alongadas na camada externa de isolamento:
duas por lateral, duas no topo, duas na base e 15 canais traseiros.
Laterais, topo e base têm somente uma divisória central de 2 mm.
Os canais traseiros não têm divisórias transversais ao longo da altura.

As duas faces da camada de isolamento continuam com 2 mm nominais.
A parede da câmara continua com 4 mm. O fechamento das cavidades acontece
no sentido de construção, com duas rampas a 45° atravessando a dimensão
estreita de 6 mm e uma ponte final de apenas 0,4 mm. Na traseira, o vão
também é de 6 mm na direção de construção; os canais têm até 6 mm de
largura para permitir esse fechamento sem um teto largo sem apoio.
Não foram abertos furos de drenagem nem acesso às cavidades fechadas.

Material sólido da região de isolamento: 541.957,92 → 432.006,24 mm³
(20,29% de redução geométrica nessa região). Essa porcentagem não é uma
estimativa de filamento nem de tempo da carcaça inteira. Os reforços
locais das passagens e as bases maciças dos M4 da caixinha continuam
integrados, com os pilotos cegos e a parede quente de 4 mm preservados.

A porta conserva sua geometria e cavidades anteriores; sua orientação
de impressão segue pendente. A orientação da carcaça está no arquivo
`output/v54/impressao_traseira_na_mesa/corpo_integrado.stl` e no projeto
Creality Print atualizado. Conferir no fatiador que não há suporte dentro
das cavidades fechadas; espessura das linhas, perímetros e configurações
de suporte precisam acompanhar a prévia de camadas. Não há G-code nesta
revisão nem comprovação física de estanqueidade ou impressão sem suporte.

Relatório das cavidades: `output/v54/insulation_geometry_report.json`;
coordenadas das cavidades: `output/v54/body_insulation_layout.json`.


Validação final v54: corpo único válido; 60 pares rígidos sem colisões;
movimentos discretos da porta e da lingueta, entrada do inox, retirada
da caixinha e barreiras maciças dos pilotos M4 conferidos pelo gerador.
As faces inclinadas de todas as 23 cavidades foram verificadas: 45° e
ponte final máxima de 0,4 mm. Todos os 36 STL cabem na K1C com margem
de 5 mm. O projeto 3MF tem escala 1:1 e 36 bandejas; leitura nativa
no Creality Print 7.2.1 terminou com saída 0 e 36 malhas manifold.
Somente `corpo_integrado.stl` mudou: os outros 35 STL são idênticos
aos da v53, inclusive a porta. Volume sólido da carcaça inteira:
1.039.699,88 → 929.166,62 mm³, redução de 10,63% pelo STL.
Essa medida exclui suportes e não é consumo calculado pelo fatiador.
Visualizador WebGL e controles conferidos; sem fatiamento ou ensaio físico.


## Apoios das dobradiças para impressão traseira — v55

Os dois apoios fixos da carcaça receberam reforços externos integrados,
com rampa a 45° na direção de construção −Y. O contorno de apoio é
X/Y [(128,−6), (136,−6), (136,6), (128,14)], com 8 mm de altura em Z
por dobradiça. A parte visível começa na lateral X130/Y12 e cresce até
X136/Y6; o trecho posterior entra 2 mm na lateral para formar a união.
O apoio sustenta a metade traseira do anel até sua seção mais larga.

Eixos e furos das dobradiças, buchas e parafusos M4×20 continuam nas
mesmas posições. A amostra da base ganhou material até a origem da
rampa para reproduzir o apoio desde a primeira camada. A carcaça
continua sendo uma peça, com a traseira Y125 apoiada na mesa; não
foram criadas aberturas nas paredes da câmara. Os furos e outros
detalhes ainda exigem conferência das camadas no fatiador.


Validação v55: corpo único válido; 60 pares rígidos sem colisão;
porta conferida em 20 ângulos entre 0° e 110°, além dos testes da
lingueta e do acesso/retirada da caixinha. Os 36 STL cabem na K1C;
3MF com 36 bandejas e escala 1:1, leitura nativa do Creality Print
7.2.1 com saída 0 e 36 malhas manifold. Visualizador WebGL e corte
conferidos. Somente o corpo e a amostra da base da dobradiça mudaram;
os outros 34 STL são idênticos aos da v54. Fatiamento não realizado.


## Gavetas capturadas e lâminas com retenção — v56

O suporte removível tem duas laterais de 3 mm com janelas, postes
frontais de 6 mm e traseiros de 7 mm de profundidade. Os apoios de
4,3 mm foram substituídos por trilhos em C de 6 mm: há apoio inferior,
limitação lateral e retenção superior. A gaveta tem 0,4 mm de folga
por lado, 0,6 mm de folga vertical e pelo menos 5,2 mm de apoio lateral
na região reta mesmo no limite da folga. A base passou de 2 para 3 mm.
O puxador foi recuado nas extremidades para passar entre as guias.
A gaveta entra e sai pela frente; para retirar completamente, continue
puxando até que ela deixe os trilhos. A retenção lateral vale enquanto
a gaveta está engatada, não depois da remoção completa.

As antigas referências de 80 × 30 × 3 mm foram corrigidas para lâmina
comum de microscopia. Encaixe nominal interno 76,8 × 26,8 mm, com altura
livre de 1,6 mm. Conferidas lâminas 76 × 26 e 75 × 25 mm, espessuras
0,9, 1,0 e 1,2 mm, inclusive posições laterais extremas. Referência
visual de 76 × 26 × 1 mm. Fontes: [Kasvi, 26 × 76 mm e 1,0–1,2 mm](https://drive.kasvi.com.br/wp-content/uploads/2023/09/Kasvi-Catalogo-2023.pdf)
e [Corning, 75 × 25 mm e 0,9–1,1 mm](https://ecatalog.corning.com/life-sciences/b2c/US/en/General-Labware/Slides/Corning%C2%AE-Plain-Microscope-Slide/p/2947-75X25).

Guias sobre as duas extremidades, batente traseiro e lingueta frontal
integral impedem a saída da lâmina. A área central fica livre. Para
colocar ou retirar: remova a gaveta, pressione a lingueta com o dedo
e deslize a lâmina pela frente das guias. Para inserir, coloque-a plana
na área dianteira e empurre até o batente; solte a lingueta. A lingueta
é uma flexura de 4 × 3 mm, com 23,8 mm de comprimento livre e ressalto
de 1,2 mm; não há presilha separada. Não foi simulada a deformação
do material: esforço, elasticidade, resistência e encaixe impresso
precisam de teste físico com a lâmina e o filamento reais.

As janelas do suporte fecham a 45° em direção à frente, com ponte
final de 0,4 mm, para sua orientação com a traseira apoiada na mesa.
Trilhos e batentes começam no plano traseiro, evitando inícios soltos.
As gavetas conservam a base plana para impressão; conferir os pequenos
avanços das guias de lâmina na prévia de camadas. Sem fatiamento nesta
revisão. A carcaça, a porta e suas vedações permanecem idênticas à v55.

Validação: 60 pares rígidos sem colisão; três gavetas extraídas em
0, 5, 15, 30, 50, 72 e 80 mm com porta a 110°; deslocamento lateral
e elevação livres dentro das folgas e bloqueados fora delas. As
lâminas entram com a lingueta liberada e encontram os batentes ao
tentar avançar, recuar ou levantar após assentadas. STL válidos,
36 bandejas no projeto 3MF em escala 1:1 e dimensões compatíveis
com K1C. Relatório: `output/v56/tray_retention_report.json`.


Leitura nativa Creality Print 7.2.1: saída 0, 36 malhas manifold;
visualizador WebGL, controles e prévias dos trilhos e da lâmina
conferidos. Alterados somente o suporte removível e três gavetas;
os outros 32 STL são idênticos aos da v55.


## Guias abertas e apoio da lâmina somente por baixo — v57

As tampas superiores dos trilhos em C foram retiradas. Cada gaveta
apoia em dois trilhos abertos em L, com entrada chanfrada de 2 mm.
A largura da gaveta passa a 102,2 mm, centralizada em X8,9; folga
lateral de 0,8 mm por lado. Apoios inferiores de 6 mm, com pelo menos
4,4 mm de sobreposição na região reta no limite da folga lateral.
As laterais reforçadas de 3 mm e o batente traseiro são mantidos.
Não há encaixe superior estreito a alinhar: apoie a gaveta nas guias
e deslize para trás. Ela pode levantar livremente; a limitação lateral
vale enquanto assentada. Base da gaveta continua com 3 mm.

Todas as presilhas e a lingueta da lâmina foram eliminadas. A própria
base recebe um alojamento raso de 76,8 × 26,8 mm e 0,6 mm de profundidade,
com cantos R0,5. Restam 2,4 mm de material nos apoios inferiores,
além do espaço central vazado. A lâmina apoia somente por baixo,
com limites periféricos laterais; nenhuma parte invade sua projeção
por cima. Coloque e retire a lâmina verticalmente. O rebaixo limita
o deslizamento horizontal enquanto ela está assentada, mas permite
elevação livre e não a prende quando a gaveta é invertida.

Conferidas lâminas 76 × 26 e 75 × 25 mm, com espessuras 0,9, 1 e 1,2 mm.
Um envelope vertical contínuo de 40 mm sobre cada lâmina não encontra
material da própria gaveta. Apoio inferior e limites nas quatro direções
horizontais conferidos. As três gavetas têm extração em 0, 5, 15, 30,
50, 72 e 80 mm conferida com a porta a 110°, sem colisões com suporte,
carcaça, inox e porta. Folga lateral/elevação verificadas dentro dos
limites; deslocamento lateral além da folga encontra a estrutura.
Não há ensaio físico de resistência, encaixe impresso ou fatiamento.

Relatório: `output/v57/tray_retention_report.json`. Carcaça, porta,
vedações e os demais componentes continuam iguais aos da v56.


Validação final v57: corpo/conjunto válidos, 60 pares rígidos sem colisão,
36 STL compatíveis com K1C e leitura nativa Creality Print 7.2.1 com
saída 0 e 36 malhas manifold. Visualizador WebGL, controles de extração
e prévias do apoio inferior conferidos. Somente o suporte e três
gavetas mudaram; os demais 32 STL são idênticos aos da v56.
