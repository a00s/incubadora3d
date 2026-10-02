# Mini incubadora CO₂

Versão atual: **v57**, gavetas com guias abertas, entrada chanfrada e mais folga; lâminas apoiadas em alojamentos inferiores rasos, totalmente livres por cima. Carcaça, porta e vedações mantidas.

Projeto de uma incubadora compacta para impressão 3D, com modelo paramétrico
em CadQuery e visualizador HTML interativo. O corpo com entrada embutida mede 195 × 141 × 160 mm.
É um protótipo de projeto: o funcionamento térmico, a vedação e o controle
de CO₂ ainda precisam de validação física.

## Imagens

Visualizador com a incubadora fechada e os controles de inspeção.

![Incubadora fechada no visualizador, com controles e seleção de peças](docs/imagens/visualizador.png)

Porta aberta, bandejas retiradas parcialmente e tampas elevadas para visualizar o interior.

![Incubadora aberta com bandejas e tampas afastadas](docs/imagens/incubadora-aberta.png)

Corte das paredes e da porta, mostrando as cavidades internas e a disposição das peças.

![Corte da incubadora com bandejas, compartimentos e paredes com cavidades de ar](docs/imagens/corte-interno.png)

## Como funciona

A câmara contém três bandejas e um reservatório de água. A lateral reúne
o compartimento de mistura e sensor de CO₂ e o espaço da eletrônica.
O gás chega pela conexão de mangueira e passa para a câmara por um furo
interno Ø5,6 mm. Esse furo não impede o retorno de umidade ao sensor.

A porta usa uma junta TPU, dobradiças e uma lingueta central com pega
para os dedos. O manípulo regula a pressão sobre a junta. As roscas do
fecho são integradas à base. O teto do CO₂ agora é fechado e integrado
ao corpo, com somente a abertura do sensor.
A tampa lateral permite acesso para manutenção; a traseira da tampa e
do corpo termina no mesmo plano. A caixa de alimentação é uma peça removível.

O repositório gera a geometria e os arquivos para revisão e impressão.
Não inclui firmware de controle nem um procedimento de operação biológica.

## Como iniciar

Para visualizar, abra [output/visualizador.html](output/visualizador.html)
em um navegador atualizado. O arquivo já contém o modelo e funciona offline.

- Arraste para girar e use **Zoom** para aproximar.
- Ative **Corte das paredes e porta** e ajuste **Altura do corte**.
- Em **Peças**, selecione componentes ou use **Isolar**.
- Para visualizar a abertura, selecione **Fecho → Afrouxado e girado 90°**
  e ajuste **Abrir porta**. A retirada das bandejas é liberada a partir de 90°.

Esses controles ajudam a inspecionar o desenho; não comprovam o funcionamento mecânico.

## Gerar o modelo e o HTML

Com Python 3.12 e o módulo `venv` disponíveis, execute na pasta do projeto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python cad/model.py
.venv/bin/python cad/check_k1c.py
.venv/bin/python cad/build_viewer.py
```

O gerador faz verificações estáticas de geometria e interferências.
Os testes de movimento ficam desativados por padrão.
O verificador K1C confere dimensões e centraliza cada STL na mesa;
a orientação final e os suportes devem ser definidos no fatiador.

Para acessar o visualizador por outro computador, publique apenas o HTML
em uma pasta dedicada, usando uma porta livre, por exemplo 8081:

```bash
mkdir -p /tmp/incubadora3d-viewer
cp output/visualizador.html /tmp/incubadora3d-viewer/index.html
python3 -m http.server 8081 --bind 0.0.0.0 --directory /tmp/incubadora3d-viewer
```

Acesse `http://IP_DO_SERVIDOR:8081/`. A porta precisa estar acessível na rede.
Se já houver um servidor nessa porta, basta atualizar o HTML servido.

## Arquivos do projeto

- `cad/model.py`: dimensões, peças e verificações estáticas.
- `cad/viewer-template.html`: controles e renderização do visualizador.
- `cad/build_viewer.py`: geração do HTML independente e do fragmento embutível.
- `cad/check_k1c.py`: conferência dimensional dos STL para a K1C.
- `output/v57/`: conjunto STEP, STL por peça, parâmetros e relatórios atuais.
- `output/visualizador.html`: visualizador pronto para abrir.
- [STATUS.md](STATUS.md): situação técnica e pendências do protótipo.

As alterações do projeto podem ser consultadas no histórico do Git.

### Ajuste da tampa de manutenção — v36

A tampa externa de CO₂/eletrônica usa **um M4×12 metálico na parte inferior
traseira**, diretamente no plástico, sem porca. O furo da tampa é Ø4,4 mm;
o apoio no corpo tem furo cego Ø3,5 mm × 9,9 mm. O centro fica 5,5 mm acima
da borda inferior da tampa. O apoio é pequeno e integrado ao piso da
caixa de eletrônica, abaixo da PCB. Não há suporte superior. O apoio tem 11,5 mm de altura; uma folga local
no piso recebe o reforço da tampa sem alterar sua borda inferior.

A cabeça fica dentro de um rebaixo Ø8,5 mm × 4,2 mm; um reforço local cresce
para dentro da tampa, preservando a face traseira em Y125. Confira as
medidas da cabeça do parafuso real. Para manutenção, remova o parafuso e
levante a tampa. Confira encaixe e retenção com o novo filamento, sem
forçar o aperto.

Os quatro pinos frágeis foram removidos; as guias têm mais folga e a folga
da saia é de pelo menos 0,4 mm por lado. As paredes e a tampa vedada do
misturador foram preservadas. As peças alteradas são somente o corpo
integrado e a tampa de manutenção; os demais STLs são os da v32.

A tampa também tem duas linguetas largas de 8 × 3,5 × 1,5 mm, com pontas
chanfradas, que entram em alojamentos cegos no teto da região seca.
Encaixe-as ao baixar a tampa e depois aperte o M4 inferior. Há 0,4 mm
de folga por lado e 0,2 mm no fundo; o encaixe alinha e apoia a tampa,
enquanto o parafuso faz a retenção. As linguetas substituem a função dos
pinos frágeis, sem alterar a posição do parafuso nem a vedação das câmaras.

## RJ45 e eletrônica — v37

RJ45 rebaixado: centro em Z32 mm, abertura de Z22,345 a Z41,655 mm.
Alívio interno de inserção entre Z18,5 e Z45,5 mm, acima do apoio do
parafuso inferior (topo em Z16,5 mm). PCB e suportes elevados 30 mm;
a placa ocupa Z52 a Z95,12 mm, acima do RJ45. Mantidos parafuso, tampa
e encaixes da v36. Altura real dos componentes e corpo do keystone
ainda precisam ser conferidos com as peças físicas.

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

## Entrada externa CO₂ e amostra — v40

Entrada antiga inferior, com curva de 90° e canal Ø2,6 mm, removida.
Novo alojamento lateral externo para mangueira de silicone Ø externo
5,8 mm: encaixe Ø5,6 mm com 12 mm de profundidade e chanfro de entrada
até Ø6,2 mm. Mangueira entra no alojamento e apoia no degrau interno.
Canal reto Ø3,5 mm segue até o misturador, sem curva nem trecho cego.
Centro da entrada em Y60/Z18; eixo para fora em −X. Projeção externa
12 mm, diâmetro externo do alojamento 10 mm; reforço contínuo liga a
parede externa ao misturador, isolando o gás das cavidades de ar.

Amostra: `output/v57/amostra_entrada_CO2_mangueira_OD5p8.stl`.
Ela reproduz o alojamento, profundidade, chanfro, degrau e canal do corpo.
Teste o aperto da mangueira e a passagem de ar antes de imprimir o corpo.
A interferência nominal de 0,2 mm precisa de ensaio com o filamento e a
mangueira reais; a geometria livre não garante que o fatiamento deixe o
canal aberto. Orientação e suportes do corpo ainda serão definidos.

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
`output/v57/amostra_entrada_CO2_mangueira_OD5p8.stl`, atualizada para o
comprimento do canal traseiro. Planejamento de orientação e suportes
permanece pendente conforme a etapa combinada.

A parede curva externa tem 2,5 mm, com uma faixa mais espessa entre
Z97,5 e Z102 sob o encaixe da tampa. O piso da base permanece em 2,5 mm.

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
`output/v57/impressao_traseira_na_mesa/corpo_integrado.stl`.
Rotação −90° em X; direção de construção corresponde a −Y do CAD.
A amostra da entrada foi orientada com a boca na mesa, reproduzindo
essa direção de construção. O corpo fica com envelope 195 × 160 × 141 mm
nessa orientação. Os demais arquivos da K1C conservam a orientação CAD.

O bocal rente elimina o ressalto que afastaria a traseira da mesa; a
transição interna foi adaptada para diminuir balanços. Suportes, pontes,
roscas, canais da junta e demais detalhes exigem revisão no fatiador;
ainda não há validação de impressão inteiramente sem suportes.

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
`output/v57/amostra_fechamento_CO2_45graus_PC.stl`.
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

## Passagem interna para mangueira opcional — v44

Passagem entre compartimento CO₂ e câmara ampliada de Ø4 para Ø5,6 mm.
Mesma posição Y60/Z34, mesmo eixo X, formato circular e parede atravessada
(14 mm). O tubo é opcional e não foi acrescentado à montagem. O diâmetro
repete o encaixe da entrada para mangueira de silicone Ø externo 5,8 mm,
com interferência nominal de 0,2 mm. O reforço maciço Ø12 mm ao redor da
passagem foi mantido, isolando o canal das cavidades de isolamento.

Amostra do furo: `output/v57/amostra_passagem_interna_CO2_OD5p8.stl`.
Reproduz os 14 mm de caminho e Ø5,6 mm, com furo horizontal para testar
a impressão e o ajuste da mangueira. Demais dimensões e componentes
mantidos. Ajuste final depende de filamento, fatiamento e mangueira reais.

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
O molde já tem STL em `output/v57/molde_caixa_inox_referencia.stl`,
com fundo na mesa. Para o corpo, usar o STL específico em
`output/v57/impressao_traseira_na_mesa/corpo_integrado.stl`.
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

Arquivos atuais: `output/v57/`; projeto completo em
`output/incubadora_CrealityPrint_7.2.1.3mf`. O projeto inclui todas as
pecas, molde e amostras em bandejas separadas.

Validacao v47: 59 pares rigidos sem colisao; porta e ressalto conferidos
a 0°, 0,5°, 1°, 2°, 5°, 15°, 30°, 60°, 90° e 110°, com passagem livre
da caixa inox pela frente a 110°. Leitura nativa do 3MF no Creality Print
7.2.1.5476, CLI --info: saida 0, 32 objetos e 32 bandejas; 32 malhas
manifold. Interface grafica e fatiamento nao conferidos.
30 STLs identicos a v46; so a porta e o painel interno foram alterados.
Encaixe das linguetas em PC e estanqueidade ainda exigem teste fisico.


## Cavidades para carcaça impressa com a traseira na mesa — v57

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
`output/v57/impressao_traseira_na_mesa/corpo_integrado.stl` e no projeto
Creality Print atualizado. Conferir no fatiador que não há suporte dentro
das cavidades fechadas; espessura das linhas, perímetros e configurações
de suporte precisam acompanhar a prévia de camadas. Não há G-code nesta
revisão nem comprovação física de estanqueidade ou impressão sem suporte.

Relatório das cavidades: `output/v57/insulation_geometry_report.json`;
coordenadas das cavidades: `output/v57/body_insulation_layout.json`.


Validação final v57: corpo único válido; 60 pares rígidos sem colisões;
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


## Apoios das dobradiças para impressão traseira — v57

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


Validação v57: corpo único válido; 60 pares rígidos sem colisão;
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
