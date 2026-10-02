
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

Leitura nativa validada no Creality Print 7.2.1.5476 oficial com `--info`: saida 0, 32 objetos e 32 bandejas; todas as malhas manifold. Interface grafica e fatiamento nao conferidos. Registro: `creality721_teste_projeto.log`.
