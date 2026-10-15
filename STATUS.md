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

## Bucha redonda: ajuste para TPU 85A e união superior reforçada

- Feedback físico: pequena folga no sensor; flange superior se separou ao
  retirar suportes, mesmo impressa com a flange maior apoiada na mesa.
- Lábios internos Ø15,4 → Ø15,2 mm. União superior reforçada internamente,
  parede de até 1,7 mm e sobreposição axial de 1,6 mm, com transição gradual.
- Inclinação dos lábios internos e externos invertida: nascem apoiados no
  corpo durante a impressão com a flange na mesa.
- STL/STEP individuais nessa orientação; 3MF atualizado nas bandejas 15, 23 e
  24. Suportes desativados somente nesses três objetos; demais ajustes preservados.
- Furo do teto e posição montada do sensor preservados. Novo ensaio físico pendente.
- Conferidos 45 cortes CAD a cada 0,2 mm: crescimento radial de até 45°, sem
  início suspenso dos lábios. Fatiamento geométrico da bandeja 15 no Creality
  Print 7.2.1: 44 camadas, 9 mm de altura, nenhum suporte no G-code de teste.

## Vedação removível da porta e rolhas em eSUN TPU-LW

- Fotos da montagem: manter a junta da caixa instalada, sem removê-la ou forçar
  o PC quebradiço. Alterar somente a junta removível da porta e as rolhas dos fios.
- Retenção no canal em V existente, pé flexível com entrada gradual; ligação
  recuada e bulbo com cavidade fechada.
  Contato na face frontal robusta em Y=0, sem depender da borda fina quebrada.
- Projeção nominal: 0,65 mm no fecho, 0,25 mm na dobradiça (X120).
- Rolhas para os fios existentes: corpo Ø12,24 no furo Ø12; canais 0,16 mm menores
  que os fios. Contato contínuo comprimido e metades bipartidas.
- Os dois projetos completos preservam as demais peças, os três perfis e o
  processo global salvos; perfil exclusivo eSUN TPU-LW acrescentado.
- Imprimir por `output/v59/vedacoes_eSUN_TPU_LW.3mf`: seis bandejas individuais,
  amostra 1, junta da porta 2, aquecedor A/B 3/4, sensor lateral A/B 5/6.
- Perfil inicial: 230 °C, mesa 50 °C, 25 mm/s, retração/wipe/Z-hop zero;
  ventilador 100% após a primeira camada, sem suportes. Fluxo 0,70 experimental:
  calibrar na amostra antes da junta inteira. Secar 55 °C por mais de 4 h.
- Guia: [VEDACAO_TPU_LW.md](output/v59/VEDACAO_TPU_LW.md).
- Compressão, força de fechamento e redução de vazamento de CO₂ pendem de ensaio.

Validação desta revisão: 59 pares rígidos sem colisão; 24 cortes da amostra a
0,2 mm com crescimento máximo de 45°; nenhum contato com o receptor fino.
Seis bandejas fatiadas no Creality Print 7.2.1 com extrusão a 25 mm/s, sem
retrações nem suportes no G-code de teste. Aviso de possíveis regiões suspensas
permanece na junta e na amostra: testar a amostra antes do anel inteiro.
Rolhas sem avisos. Projeto completo: 39 peças/36 bandejas, malhas e limites
K1C conferidos. Visualizador atualizado, HTTP 200 e controles verificados.

## Junta da porta com tubo oco mais alto

- Somente a junta removível da porta e sua amostra são modificadas nesta revisão.
  Junta da caixa, peças rígidas, rolhas dos cabos e perfis de impressão preservados.
- Altura total nominal: 7,25 mm no fecho e 6,05 mm na dobradiça (X120).
  Projeção contra a face Y=0: 3,0 / 1,8 mm, com redução contínua de 1,2 mm.
- Cavidade axial de 5,60 mm no fecho; trecho paralelo com paredes nominais
  de 0,55 mm. Mais espaço interno para o tubo dobrar durante a compressão.
- Retenção, ligação recuada e orientação de impressão anteriores preservadas.
- Calibrar o material e testar a amostra antes do anel inteiro. Força de
  fechamento, recuperação elástica e estanqueidade pendem de ensaio físico.

Validação do tubo alto: STL fechado e STEP válido após reimportação; 36 cortes
CAD da amostra a 0,2 mm passaram no crescimento máximo de 45°. Menor projeção
na dobradiça conferida; sem interseção com o receptor fino. Seis bandejas
fatiadas: retração zero, extrusão a 25 mm/s, aviso anterior de regiões suspensas
mantido somente na junta e na amostra. Projetos completos lidos no Creality
Print 7.2.1, limites e 36 bandejas conferidos. Visualizador: HTTP 200 e controles
sem erros. 39 STL e 37 objetos do projeto completo permanecem idênticos.

## Correção de small_perimeter_speed na interface do Creality Print

- Removida a sobrescrita escalar `small_perimeter_speed=100%` dos quatro objetos
  TPU-LW no projeto completo e dos seis objetos do projeto separado.
- No projeto separado, o valor global passa a `25` mm/s em vetor numérico.
  O valor global salvo no projeto completo permanece preservado.
- Geometria, bandejas, filamentos e demais configurações não foram alterados.
- `cad/check_lw_config.py` impede que essa sobrescrita seja reintroduzida nos arquivos.
  Leitura nativa e fatiamento das seis bandejas novamente conferidos.

## Junta sem floating regions

- Apoio do pé prolongado até Y=-3,0; parede interna da cavidade reforçada somente
  junto à raiz, mantendo uma transição contínua imprimível.
- Alturas 7,25 / 6,05 mm, tubo flexível alto, encaixe rígido e junta da caixa
  preservados. Cabos e perfis de impressão permanecem iguais.
- Detector de suportes ativo: junta inteira e amostra fatiadas sem floating
  regions, sem outros avisos e sem gerar suportes. Verificação de regressão
  passa a rejeitar qualquer aviso nas seis bandejas.
- Amostra ainda necessária para conferir o material real, o encaixe e a vedação.

Validação final desta correção: seis bandejas do arquivo separado e bandejas
16/21 do projeto completo sem qualquer aviso de regiões suspensas; detecção de
suportes ativa. G-code do arquivo separado: 25 mm/s, retração zero, sem suportes.
STEP reimportado válido, STL fechado, 36 cortes CAD e limites K1C conferidos.
Visualizador atualizado, HTTP 200 e controles sem erros. Configurações de
filamento/processo e 39 STL das demais peças preservados.

## Linha de base de perda de CO₂ — vedação antiga

- 2026-10-15, após o usuário fechar a porta com a vedação antiga reinstalada.
  CO₂ desabilitado, válvula fechada, aquecimento habilitado e meta de 37 °C.
- Após o reset para gravar o firmware, o `BOOT_COUNT` lido foi 35. Quatro janelas
  consecutivas de aproximadamente 60 s registraram **−385, −302, −363 e −298 ppm/min**.
- Durante as janelas, CO₂ caiu de 28.601 para 27.234 ppm; temperatura ficou entre
  36,7 e 37,5 °C e umidade entre 46,2 e 47,4%. O ventilador interno ligou perto de
  30 °C; aquecedor ciclou conforme a temperatura. O sensor reportou leituras válidas.
- Evidência de perda persistente com a porta fechada, mas a taxa ainda é uma
  estimativa operacional: não foi medida a concentração externa nem calibrado o
  sensor. Para comparar a vedação nova, repetir com temperatura e concentração
  inicial semelhantes e CO₂ desligado durante as janelas de medição.
- Após registrar a linha de base, o automático de CO₂ foi reativado para seguir
  em direção à meta de 50.000 ppm; a taxa seguinte já inclui injeção e não representa
  vazamento isolado.
- Com CO₂ reativado perto de 27.000 ppm, foram aplicados pulsos automáticos de
  45, 67 e 100 ms. A resposta ao pulso de 100 ms foi atrasada: a elevação máxima
  observada chegou a 172 ppm, e a janela de 60 s marcou +208 ppm/min apesar da perda.
- Depois, o controlador aplicou duas doses de 1 ms enquanto a resposta ainda era
  instável. O limite de rampa baseado em `1 + 1/2` impedia que a dose crescesse acima
  de 1 ms. Correção: piso automático de 5 ms e limite de rampa com incremento mínimo;
  compilada e gravada para a próxima dose.

## Observação adaptativa de CO₂ e correção do indicador de boots

- 2026-10-15, monitor USB aberto com o controle automático de CO₂ e aquecimento
  habilitados. O contador serial `BOOT_COUNT` marcou 37 ao iniciar o monitor; abrir
  a porta serial causa reset por DTR e também incrementa esse contador.
- A leitura caiu de aproximadamente 25.265 ppm para 24.967 ppm; a taxa em janela
  de 60 s foi −252 ppm/min. O controle aplicou 45 ms e depois 67 ms.
- A resposta ao pulso de 67 ms foi atrasada: o pico registrado após o pulso foi
  +1.006 ppm e a janela marcou +964 ppm/min. Depois o controle usou pulsos de 5 e
  7 ms; a taxa voltou para −285 ppm/min. A rampa então subiu para 10 e 15 ms,
  acompanhando a perda observada, sem extrapolar novamente para dezenas de ms.
- As janelas subsequentes marcaram −257 e −125 ppm/min. A concentração ficou perto
  de 25,2–25,5 mil ppm. Isso confirma que a dose útil muda com o tempo e que a
  resposta tardia deve permanecer separada da taxa instantânea.
- A temperatura externa variou de 36,7 a 37,7 °C com o aquecimento habilitado;
  chegou momentaneamente a 37,7 °C e depois retornou a 37,0–37,1 °C. O ventilador
  ligou quando a leitura interna chegou a 30,0 °C. CO₂, temperatura e umidade foram
  reportados válidos durante a observação.
- Corrigi o cabeçalho: a cor mantém o estado geral, sem “1 FORA/2 FORA”; o contador
  `R<n>` volta ao display. A leitura de CO₂ muda para vermelho fora da faixa e
  verde dentro; a temperatura muda para vermelho fora e mantém cor neutra dentro.
  Quando um pulso termina, as bolhas continuam animadas por 3 segundos para tornar
  visíveis os pulsos curtos. Compilado e gravado para Uno: 32.214 bytes Flash (99%),
  923 bytes RAM (45%). O reset de gravação incrementa o contador persistente uma vez.

## Retorno ao azul-marinho e animação durante aquecimento

- O teste de fundo preto foi revertido após a preferência pelo azul-marinho
  `RGB 8,18,30`, aplicado à intro, tela, leituras e áreas apagadas dos ícones.
- A intro de DNA ficou na tela durante os 10 s de aquecimento; revisão posterior
  substitui a hélice grande por pontos animados de CO₂ durante a espera, mantendo as
  animações dos três ícones principais.
- A última gravação testada ocupava 32.132/32.256 bytes de Flash e 923/2.048 bytes
  de RAM. Esta revisão compilou e foi gravada com `--verify`: 32.208/32.256 bytes
  de Flash (48 bytes livres) e 923/2.048 bytes de RAM. A gravação reinicia a placa
  e incrementa o contador persistente uma vez.
- Antes desta revisão, a leitura perto de 26.000 ppm caiu a cerca de −362 ppm/min;
  após os ciclos de espera, o controle automático abriu um pulso de 45 ms. A demora
  para atingir 5% continua como ponto de investigação, separado desta revisão visual.

## Dose automática ajustada pela resposta observada

- Monitor sem DTR, sem reiniciar a placa: perto de 26.000 ppm, a primeira janela
  registrou −313 ppm/min. Após um pulso de 45 ms, a janela seguinte ficou em
  −7 ppm/min. Com pulsos seguintes de 5 e 7 ms, a taxa voltou a −21 ppm/min; a
  concentração caiu cerca de 400 ppm ao longo de pouco mais de 3 minutos.
- O log mostrou que a taxa instantânea ruidosa fazia o cálculo voltar a 5 ms,
  mesmo após esperar o ciclo de resposta. O critério de estabilidade de 30 s não
  deve bloquear o cálculo do tamanho da dose: a espera de aproximadamente 60 s já
  permite observar a resposta do sensor.
- Revisão inicial (posteriormente revista após logs de subida atrasada): dimensionar
  o próximo pulso usando a resposta observada após o
  intervalo, sem exigir que a inclinação instantânea esteja estável. A rampa continua
  limitada a 1,5× por ciclo e os limites por proximidade ao alvo são preservados.
  No teste anterior à troca da revisão, a resposta observada levou o próximo pulso de
  45 para 67 ms e depois 100 ms; o pulso de 100 ms provocou subida rápida. Isso confirma
  a adaptação à vazão, mas exige acompanhar o atraso do sensor para evitar excesso.
- A temperatura chegou a 37,7 °C enquanto o relé já estava desligado; depois caiu
  gradualmente para 37,0 °C. Alterei o termostato para ligar abaixo de 36,5 °C e cortar
  em 36,7 °C para compensar o calor residual. A histerese foi compilada e gravada nesta
  revisão; ainda precisa ser acompanhada com o aquecedor ligado para validar os picos.
- A intro de DNA grande foi removida. Os três pontos de espera reutilizam o ícone vetorial
  de CO₂, desenhado por coordenadas em 25×17 px; as animações compactas dos três controles
  permanecem. Não há bitmap de ícone no firmware.
- Firmware compilado e gravado para Uno com `--verify`: 32.068/32.256 bytes de Flash
  (188 bytes livres) e 923/2.048 bytes de RAM. O upload reiniciou a placa uma vez; o
  contador persistente de inicializações registra esse reset.

## Resposta tardia observada e pausa automática

- A abertura do monitor reiniciou a placa uma vez (contador persistente 49). No início
  do registro, CO₂ marcava 43.041 ppm, temperatura 36,5 °C, aquecimento ligado e
  controle de CO₂ ligado. A primeira dose automática após o reinício foi 45 ms a
  42.308 ppm.
- Com CO₂ a 42.316 ppm, o ciclo seguinte aplicou 67 ms. A leitura então subiu até
  48.977 ppm, com pico de taxa instantânea de +217,88 ppm/s. A janela de um minuto
  chegou a +3.442 ppm/min. O código permitiu uma dose adicional de 71 ms após apenas
  60 s, enquanto a subida ainda estava em andamento.
- Desativei o automático pela serial em 45.865 ppm. Sem novos pulsos, a leitura ainda
  subiu até cerca de 49.000 ppm e depois caiu. Isso confirma que o ciclo de 60 s pode
  acabar antes da resposta tardia; a concentração não ultrapassou 50.000 ppm neste
  ensaio. O automático permaneceu desligado ao final da coleta.
- A temperatura cortou o aquecedor em 36,7 °C, mas atingiu 37,6 °C após a inércia
  térmica; posteriormente ficou perto de 37,5 °C e desceu gradualmente. A histerese
  reduziu o pico observado anteriormente de 37,7 °C, mas ainda não mantém o alvo de
  37,0 °C com precisão. O ventilador ligou ao atingir 30 °C internamente.
- Revisão atual: após o cooldown mínimo, bloquear novas doses automáticas enquanto a
  inclinação estiver acima de 5 ppm/s (300 ppm/min). Exigir 30 s contínuos abaixo desse
  limite antes de calcular/aplicar outra dose; doses manuais continuam sendo um caminho
  explícito de intervenção. Compilado e gravado com `--verify`: 32.084/32.256 bytes de
  Flash (172 bytes livres), 923/2.048 bytes de RAM. O automático está salvo como
  desligado; validar a nova espera com a próxima ativação monitorada.

## Verificação da espera e da pressão da câmara

- Após uma nova ativação monitorada em 47.230 ppm, foram aplicados pulsos de 45 ms e,
  após o cooldown, 67 ms. A leitura do segundo pulso subiu de 46.161 para cerca de
  46.947 ppm em aproximadamente 100 s; a máxima observada até então foi +786 ppm.
  A próxima dose não saiu no fim dos 60 s: `trend_ready=0` enquanto a taxa ainda
  passava de 300 ppm/min, confirmando o bloqueio por subida.
- Depois que a subida desacelerou por 30 s, foi aplicado um pulso automático de 5 ms.
  A auditoria do loop encontrou a causa: `contador_pomp` era impresso em zero e depois
  decrementado para −1; no ciclo seguinte, o cálculo proporcional acontecia antes de
  a correção para zero, tornando a estimativa inválida e selecionando o piso de 5 ms.
  O CO₂ automático foi desligado em 46.295 ppm. A taxa líquida anterior foi
  −589 ppm/min; este valor ainda não distingue fuga física de troca de ar/transiente.
- Revisão gravada: o contador agora decrementa somente acima de zero, para que a
  estimativa proporcional seja calculada no mesmo ciclo em que o cooldown termina.
  Compilado e gravado com `--verify`: 32.070/32.256 bytes de Flash (186 bytes livres),
  923/2.048 bytes de RAM. O CO₂ automático está salvo como desligado; validar a estimativa
  corrigida na próxima ativação monitorada.
- Referências de fabricante consultadas: [Thermo Fisher Steri-Cult manual](https://assets.thermofisher.com/TFS-Assets/LED/manuals/forma-stericult-co2-incubator-usermanual-7023307.pdf)
  especifica ±0,1 °C de controle, ±0,2 °C de uniformidade e ±0,1% CO₂ a 5%;
  [Memmert ICO105](https://www.memmert.com/en/products/incubators/co2-incubator/ico105-2/pdf)
  lista sondas Pt100 redundantes, aquecimento em seis lados e calibração de fábrica
  no centro da câmara a 37 °C/5% CO₂. O [manual Thermo Heracell](https://documents.thermofisher.com/TFS-Assets/LED/manuals/FILE-1907-718829-EN.pdf)
  descreve leve pressurização e saída por compensação de pressão; o [manual Thermo BBD](https://tools.thermofisher.com/content/sfs/manuals/D21735~.pdf)
  especifica um respiro para impedir acumulação indesejada de pressão.
- Comparação prática: nossa leitura exterior variou de 36,1 a 37,5 °C no aquecimento,
  com pico observado 0,5 °C acima da meta. Não há ainda calibração contra termômetro
  rastreável nem mapa de uniformidade; portanto, não é possível comparar precisão real
  com as especificações comerciais. A câmara deve permanecer ventilada/compensada, não
  hermeticamente pressurizada.
- A telemetria desta rodada marcou 52–54% RH a aproximadamente 37 °C. O valor ainda
  precisa ser conferido com higrômetro independente; se confirmado, está bem abaixo do
  sistema de umidificação de 95% RH a 37 °C especificado no manual Steri-Cult.
- Auditoria do CAD: não há canal de compensação de pressão dedicado à câmara. O respiro
  Ø0,8 mm da junta TPU atravessa apenas a pele externa do bulbo e não comunica com a
  câmara. Não abrir um furo sem restrição/filtro: antes de apertar mais a porta, definir
  um componente de compensação adequado e seu ponto de instalação. Pela câmara nominal
  de 112×132×111 mm, o volume é cerca de 1,64 L; em uma conta idealizada sem saída de
  gás, atingir 5% a partir do ar ambiente exigiria acrescentar ~86 mL de CO₂ e elevaria
  a pressão em ~5,3 kPa, aplicando ~78 N na área frontal de 112×132 mm. Isso não é uma
  classificação de pressão da peça.
- O ventilador acionou em 30 °C na sonda secundária e manteve a leitura perto de
  29,5–30 °C durante a coleta; não houve prova de que chegaria abaixo de 29 °C para
  desligar. O limiar liga/desliga 30/29 °C é conservador, mas falta confirmar a posição
  da sonda e medir a resposta térmica do compartimento com o ventilador ativo.

## Amostra ao vivo de temperatura, ventilador e taxa de CO₂

- 2026-10-15, monitor serial aberto em PTY com `sg dialout`; a abertura reiniciou a
  placa e o `BOOT_COUNT` passou a 54. CO₂ automático estava desligado, aquecimento
  automático ligado, válvula fechada.
- Durante cerca de 92 s de telemetria após a inicialização, CO₂ caiu de 43.070 para
  42.265 ppm; a janela de 60 s reportou **−550 ppm/min**. Temperatura da câmara ficou
  entre 36,5 e 37,1 °C; sonda interna entre 29,5 e 29,7 °C. Ventilador permaneceu
  desligado, pois a sonda não atingiu 30 °C.
- O campo `ppm/min` já é desenhado na tela durante a fase de adaptação: mostra `---`
  até completar uma janela válida de aproximadamente 60 s e então exibe a taxa com
  sinal. Ele é atualizado a cada janela, sem depender de o controle automático ter
  estabilizado ou alcançado a meta. O mesmo valor está disponível na telemetria serial.

## Ciclo térmico limitado e nova semente de CO₂

- 2026-10-15. Alterei o termostato para impor intervalo mínimo de 30 s entre mudanças
  do relé, limitar cada ciclo ligado a 45 s e desligar imediatamente ao atingir 37,2 °C.
  A histerese continua ligando abaixo de 36,5 °C e desligando em 36,7 °C. No primeiro
  ciclo observado após a gravação, o relé desligou pelo limite de 45 s com leitura de
  36,4 °C; a temperatura chegou a 36,9 °C e permaneceu entre 36,9–37,0 °C por cerca de
  um minuto. É um resultado preliminar, ainda sem ciclo longo ou termômetro de referência.
- Para compensar a perda observada, elevei a semente do pulso automático de 30 para
  60 ms; a rampa limitada a 1,5× solicita 90 ms no primeiro ciclo. Um pulso de 90 ms
  foi aplicado perto de 29.452 ppm e a leitura estava em 29.166 ppm cerca de 57 s depois.
  O teste foi interrompido antes de completar a janela de resposta porque a porta seria
  aberta para troca da vedação; portanto, esse ponto não mede a resposta do pulso.
  O controle automático e o aquecedor foram desligados antes da intervenção.
- Para manter a margem de Flash do Uno, os desenhos de ventilador, chama e bolhas foram
  simplificados para ícones estáticos; as bolhas ainda aparecem por 3 s após um pulso.
  A compilação e a gravação com verificação foram concluídas: 32.008/32.256 bytes de
  Flash (248 bytes livres) e 926/2.048 bytes de RAM. A revisão do firmware e desta
  documentação precisa ser enviada ao Git.

## Vedação nova, taxa de perda e retorno das animações

- 2026-10-15, após o usuário instalar a vedação nova e fechar a porta. CO₂ automático
  permaneceu desligado, válvula fechada. O monitor serial normal reportou `BOOT_COUNT,64`;
  sessões seriais abertas durante a coleta reiniciam a placa e incrementam esse contador.
- A comparação começou com a câmara ainda fria, a 33,1 °C e 27.136 ppm. O aquecimento
  foi habilitado para aproximar as condições da linha de base antiga; a temperatura
  atingiu 37,5 °C e depois oscilou entre 36,3 e 37,5 °C nos ciclos observados. A umidade
  medida variou de 43,0 a 45,3% RH. O ventilador acionou ao redor de 30 °C na sonda interna.
- Em cerca de 7,5 min, o CO₂ caiu de 27.136 para 24.744 ppm. As janelas de taxa válidas
  registraram **−336, −326, −339, −328, −299, −307 e −296 ppm/min**. A linha de base da vedação
  antiga foi −385, −302, −363 e −298 ppm/min, com média −337. As taxas continuam na mesma
  faixa; como concentração inicial, temperatura e umidade não foram exatamente pareadas,
  este ensaio não mostra redução clara do vazamento após a troca.
- A tentativa de capturar via `socat` produziu bytes corrompidos no terminal após um
  comando de aquecimento; ela foi encerrada e substituída pelo monitor Arduino CLI, que
  voltou a produzir linhas `DATA` válidas. Os dados acima vêm do monitor normal.
- Para recuperar movimento nos três ícones, removi `verifyAutoCalibration()`: a função
  não enviava a consulta que dizia verificar, esperava 500 ms e interpretava bytes
  residuais sem garantir que o buffer de resposta estivesse preenchido. Mantive o comando
  de desativação da calibração automática e o descarte da resposta. As animações compactas
  de CO₂, chama e ventilador foram restauradas. Compilação e gravação com verificação:
  32.120/32.256 bytes de Flash (136 livres), 825/2.048 bytes de RAM.
- Após a gravação, o monitor confirmou inicialização normal e `BOOT_COUNT,66`. CO₂ ficou
  desabilitado, aquecimento habilitado e válvula fechada. Em duas janelas após o reinício,
  as taxas foram −269 e −292 ppm/min, com temperatura entre 36,4 e 37,1 °C e umidade de
  45,5–46,0% RH. A sonda interna ficou em 29,1–29,5 °C. A taxa de −292 ppm/min perto de
  23.700 ppm continua compatível com a perda anterior; não confirma melhora da vedação.
  A tela não foi fotografada após restaurar as animações, então a aparência física ainda
  precisa de confirmação visual.

## Continuação da observação de umidade após troca da vedação

- 2026-10-15, continuação da mesma sessão serial (`BOOT_COUNT` permanece 66; sem novo
  reset). CO₂ automático desligado, aquecimento automático ligado, válvula fechada.
- Em cerca de 2 min, CO₂ caiu de 23.371 para 23.134 ppm; as amostras intermediárias
  foram monotônicas e a janela móvel publicada ficou em −290 ppm/min. Temperatura
  variou de 36,3 a 36,8 °C; umidade relativa subiu de 46,7 para 47,1%; sonda interna
  ficou em 29,6–29,7 °C. O relé de aquecimento alternou durante o período.
- Esse trecho não prova que a vedação melhorou nem que a umidade aumentou por causa da
  vedação: não houve umidade ambiente de referência e as condições de temperatura e
  concentração variam. Guardar 46,7–47,1% RH como leitura anterior à instalação do
  recipiente de água maior, a ser comparada em condições semelhantes.
- Continuação da mesma sessão: a janela seguinte atualizou a taxa para −306 ppm/min
  perto de 23.055 ppm. Temperatura voltou a 37,0 °C; RH oscilou entre 46,8 e 46,5%.
  A oscilação reforça que a comparação do recipiente maior deve usar um trecho após
  estabilização térmica, e não somente a tendência inicial de umidade.

## Janela longa da mesma sessão: estabilidade térmica e perda de CO₂

- Sem novo reset desde `BOOT_COUNT,66`; CO₂ automático desligado, aquecimento automático
  ligado e válvula fechada. Entre aproximadamente 23.055 e 22.696 ppm, a taxa foi
  atualizada de −306 para −301 ppm/min. A queda ao longo do trecho é compatível com
  essa taxa; o número de taxa só muda quando fecha a janela de cálculo.
- Em cerca de 3 min adicionais, a temperatura da câmara ficou entre 36,5 e 37,0 °C,
  enquanto o relé alternou sem acionamento contínuo; a sonda interna ficou em 29,7–29,9 °C.
  RH permaneceu entre 46,3 e 46,7%. É evidência preliminar de controle térmico próximo
  à meta neste trecho, não uma validação independente de precisão nem uniformidade.
- Comparar a leitura de RH com a do recipiente maior depois de aguardar a temperatura
  estabilizar. A leitura atual de 46,3–46,7% é a referência local imediatamente anterior.
- Janela seguinte da mesma sessão (10:35 UTC): CO₂ chegou a 22.443 ppm e a taxa foi
  recalculada para −271 ppm/min em 22.474 ppm. RH ficou em 47,5–47,7%; a temperatura
  variou de 36,3 a 36,7 °C. A sonda interna alcançou 30,0 °C e o ventilador ligou; o
  aquecedor desligou ao passar por 36,5 °C, conforme a histerese observada. Os dois
  estados coexistiram por um intervalo curto, sem evidência aqui de erro de controle.

## Ajuste experimental do controle térmico e referência antes do anel do sensor

- 2026-10-15. Para aproximar a leitura da meta de 37 °C após ciclos observados entre
  36,3 e 37,0 °C, o termostato foi ajustado de 36,5/36,7 °C para ligar até 36,8 °C e
  desligar a partir de 37,0 °C. O intervalo mínimo entre mudanças e o limite de cada
  acionamento passaram de 30/45 s para 20/20 s; o corte de segurança permaneceu em
  37,2 °C.
- Compilado e gravado com `--verify`: 32.120/32.256 bytes de Flash e 825/2.048 bytes
  de RAM. O monitor após a gravação confirmou inicialização e `BOOT_COUNT,68`; CO₂
  automático permaneceu desligado e válvula fechada.
- Primeira observação ainda é transitória: após o reset a leitura caiu de 36,5 para
  36,0 °C, depois ficou entre 36,6 e 37,3 °C. Em um pulso de 20 s, o sensor mostrou
  subida residual até 37,3 °C com o relé já desligado; nos ciclos seguintes ficou
  em torno de 36,6–36,9 °C. Isso sugere que o centro da leitura se aproximou de 37 °C,
  mas ainda há inércia e o ensaio não fecha estabilidade em longo prazo. Não aumentar
  mais a energia do aquecedor sem observar uma janela maior.
- Referência de perda da câmara após instalar a vedação nova da porta e antes de instalar
  o anel novo do sensor: válvula fechada, temperatura estabilizada perto de 36,8–36,9 °C,
  leitura de CO₂ próxima de 20.032 ppm e janela de aproximadamente −305 ppm/min. A taxa
  perto de 20.000 ppm é menor em valor absoluto que a medida a 26.000–28.000 ppm, como
  esperado para uma mesma troca proporcional com o ar ambiente.
- Normalizando aproximadamente por excesso sobre 420 ppm ambiente, a constante observada
  é ~0,0123/min com a vedação antiga (−337 ppm/min em ~27.918 ppm), ~0,0125/min com a
  vedação nova da porta (−319 ppm/min em ~25.940 ppm) e ~0,0155/min na janela atual antes
  do anel (−305 ppm/min em ~20.032 ppm). Os ensaios não são pareados nem calibrados; não
  demonstram melhora da porta. Repetir depois da instalação do anel em temperatura e
  concentração semelhantes para avaliar o efeito do conjunto, sem atribuir a fuga a uma
  localização específica.
- Continuação da referência antes do anel, sem reset e ainda com a vedação nova da porta:
  a janela seguinte marcou −218 ppm/min perto de 19.610 ppm; temperatura ficou em 37,1 °C,
  RH em 48,2–48,3% e aquecedor desligado. A constante aproximada, usando 420 ppm como
  ambiente, é ~0,0113/min. Continua na mesma ordem das referências com vedação antiga e
  nova; a leitura adicional não muda a conclusão de que a vedação da porta ainda não
  demonstrou redução clara. Após instalar o anel, repetir a janela perto de 37 °C.

## Primeiro indício após instalar o anel do sensor (encaixe ainda frouxo)

- 2026-10-15, após retirar e recolocar o sensor para experimentar o anel ainda com folga.
  Os atuadores permaneceram desligados e a válvula fechada. A leitura caiu transitoriamente
  de ~19.200 para ~2.000 ppm e depois subiu até ~16.260 ppm; toda essa recuperação foi
  excluída da medição de perda.
- Após a leitura se estabilizar perto de 16.260 ppm, uma janela completa caiu de cerca de
  16.260 para 16.139 ppm em ~61 s: **−119 ppm/min**. A temperatura caiu de 34,2 para
  33,5 °C durante a janela e RH subiu de 51,9 para 53,0%; o aquecimento estava desligado.
- Normalização aproximada por excesso sobre 420 ppm: ~0,0076/min nesta janela, contra
  ~0,0113/min antes do anel (−218 ppm/min perto de 19.610 ppm). Isso sugeriria ~33% menos
  perda fracionária, mas a comparação não está controlada: a câmara foi aberta, o sensor
  foi movido, a temperatura estava vários graus mais baixa e o encaixe ainda tem folga.
  Tratar apenas como indício inicial; repetir com o anel justo e a temperatura estabilizada
  perto de 37 °C antes de concluir se houve melhora.
- Segunda janela consecutiva após o assentamento do sensor marcou −141 ppm/min perto de
  15.995 ppm, com a câmara a 32,8 °C e ainda esfriando. Usando o mesmo modelo simples
  (excesso sobre 420 ppm), as duas janelas pós-anel têm constantes ~0,0076 e ~0,0091/min,
  média ~0,0083/min, cerca de 27% abaixo de ~0,0113/min antes do anel. Há um indício
  repetido de melhora mesmo com folga, mas o teste começou após retirar/recolocar o sensor
  e a câmara não estava a 37 °C; não é confirmação. O CO₂ e o aquecimento seguem desligados.
- Atualização posterior do mesmo ensaio frouxo: duas janelas adicionais marcaram −169 ppm/min
  perto de 15.822 ppm e −145 ppm/min perto de 15.674 ppm, com temperatura caindo de 32,2
  para 31,6 °C e RH subindo de 55,1 para 56,0%. Constantes aproximadas: ~0,0110 e
  ~0,0095/min, média ~0,0102/min, somente ~10% abaixo da referência pré-anel (~0,0113/min).
  Portanto, o ganho aparente de ~27% das primeiras janelas não persistiu; a leitura após
  remoção/recolocação ainda estava se acomodando e a temperatura continuava mudando. O
  encaixe frouxo não demonstra melhora mensurável. Repetir com o anel final e a câmara
  estabilizada perto de 37 °C.
- Terceira janela posterior ao anel frouxo: −153 ppm/min perto de 15.517 ppm, com a
  temperatura em 31,1–31,0 °C. A constante aproximada é ~0,0101/min, coerente com as
  duas janelas anteriores e ainda próxima da linha de base (~0,0113/min). O resultado
  reforça que não há melhora clara demonstrada; a câmara segue fria e fora das condições
  de comparação pretendidas.

## Resposta do CO₂ e aquecimento após reinstalar o sensor

- 2026-10-15. O sensor foi recolocado no anel ainda com folga. Após a recuperação da
  leitura ambiente (~706 ppm), o CO₂ subiu até ~10.000 ppm sem injeção; aguardamos a
  taxa cair antes de ligar o automático. Este trecho inicial é acomodação do sensor e
  não serve como ensaio de vedação.
- Com o aquecedor habilitado, a câmara subiu de ~28,7 °C para ~36,9 °C em cerca de
  9,5 min. O relé operou em ciclos limitados a 20 s; a leitura chegou momentaneamente
  a 37,2 °C com o relé já desligado, mostrando inércia térmica residual. Depois se
  manteve perto de 36,5–37,1 °C enquanto o controle permaneceu habilitado.
- Com o CO₂ automático ligado e alvo de 50.000 ppm, os pulsos observados foram 90,
  135, 202, 303 e 93 ms. Os primeiros dois não produziram resposta clara imediatamente;
  após os pulsos seguintes, o sensor mostrou resposta atrasada e acumulada. Um pulso de
  303 ms partiu de ~18.000 ppm e a leitura alcançou ~37.900 ppm durante a resposta; o
  firmware registrou aumento máximo de ~20.015 ppm desde esse pulso. Após o pulso de
  93 ms, a leitura chegou a ~39.294 ppm. O alvo de 50.000 ppm não foi atingido nesta
  sessão. Não atribuir todo o ganho a um único pulso: os trechos de resposta se
  sobrepõem e a pressão do reservatório varia.
- O firmware manteve a válvula fechada enquanto a concentração continuava subindo; só
  liberou nova dose após a tendência desacelerar e ficar estável. A taxa de janela
  chegou a +9.586 ppm/min durante a recuperação e depois caiu para +271 ppm/min antes
  da última dose. Essa resposta confirma que um integrador convencional atualizado a
  cada leitura poderia acumular comando durante o atraso; preservar espera de resposta,
  limites de pulso e anti-windup ao avaliar PID para CO₂.
- Para encerrar a intervenção antes da atualização do projeto, CO₂ e aquecimento foram
  desligados por comando serial; a serial confirmou válvula e aquecedor desligados. Cerca
  de 126 s depois, STATUS mostrou 38.510 ppm, 35,4 °C, RH 50,9%, ventilador ligado e
  taxa móvel de −300 ppm/min. Como o anel ainda tinha folga e a temperatura estava
  mudando, essa queda não é comparação válida de vazamento.
- O teste de temperatura mostra resposta lenta e pequena ultrapassagem após desligar o
  aquecedor. Antes de adicionar PID, registrar mais ciclos nas mesmas condições; para
  temperatura, limitar integral e comutar o aquecedor com proteção de tempo mínimo e
  corte independente. Para CO₂, preferir ganho proporcional/adaptativo por dose e
  janela de assentamento; qualquer componente integral precisa congelar durante a
  resposta pós-pulso. Não foram alterados nem gravados parâmetros de controle nesta
  sessão.

## Semântica do trend_ready durante queda de CO₂

- 2026-10-15. A serial mostrou `rate_ppm_s=-11,47` e `trend_ready=1` durante queda
  rápida de CO₂. Primeiro interpretamos `trend_ready` como taxa absoluta próxima de
  zero e fizemos uma versão simétrica (`-5..+5 ppm/s`) no commit 773f9f4.
- A revisão do algoritmo mostrou que esse indicador libera nova dose após a resposta
  positiva atrasada do pulso anterior. O perigo que se quer evitar é empilhar doses
  enquanto o sensor ainda registra uma subida tardia. Uma taxa negativa forte indica
  perda de CO₂; após o cooldown mínimo de ~60 s, isso pode exigir compensação. Impor
  taxa absoluta pequena bloquearia a reposição durante uma fuga persistente.
- A condição simétrica foi revertida: o firmware volta a considerar a tendência pronta
  quando `co2Rate <= +5 ppm/s` por 30 s, com o cooldown mínimo preservado. Isso não
  declara uma queda rápida “plana”; significa apenas que não há subida positiva acima
  do limite. A taxa assinada continua disponível na tela e na telemetria. Revalidar em
  um ciclo com o sensor reinstalado, CO₂ abaixo da meta e vazão de queda conhecida.
- A versão simétrica compilou e foi gravada, mas a observação de queda após boot não
  comprovou se ela era melhor para a incubadora; foi revertida antes de continuar o
  ensaio. O teste de bancada será repetido com a semântica anterior. Controles estavam
  desligados e válvula fechada durante esta revisão.
- Revisão restaurada compilada para Uno: 32.120/32.256 bytes de Flash e 825/2.048
  bytes de RAM. Upload com verificação terminou sem erro. A reconexão serial após o
  upload confirmou `BOOT_COUNT=72`, `co2_enabled=0`, `heater_enabled=0`, `valve_open=0`
  e `heater_on=0`; CO₂ 35.192 ppm, temperatura 30,3 °C e umidade 58,7% na última
  amostra. O sensor já apresentava queda; após o boot a janela de tendência ainda não
  estava pronta. O monitor serial foi fechado para não causar outro reset. A nova
  semântica segue sem validação dinâmica com controle ativo.

## Queda de CO₂ com saídas desligadas

- 2026-10-15. Abri o monitor serial para uma nova janela de observação; DTR reiniciou
  o Uno e o firmware reportou `BOOT_COUNT=73`. Esse incremento corresponde à conexão
  do monitor, não a um crash. Após 13,5 s de aquecimento do sensor, CO₂ caiu de
  34.718 para 34.139 ppm em 74,8 s (cerca de −464 ppm/min). A janela móvel reportou
  −468 ppm/min. A queda foi contínua, embora a taxa por amostra variasse.
- Durante toda a janela `co2_enabled=0`, `heater_enabled=0`, `valve_open=0` e
  `heater_on=0`. Temperatura lida caiu de 30,0 para 29,4 °C, umidade subiu de 59,3 para
  60,3% e temperatura interna ficou em 29,5–29,6 °C. `trend_ready` passou a 1 após
  completar a janela de assentamento, com CO₂ ainda caindo; isso confirma a semântica
  restaurada, mas não valida o ciclo de dosagem sob controle ativo.
- O novo anel ainda não foi confirmado como instalado nesta medição. Portanto este é
  um baseline do estado físico atual, não uma comparação do anel novo nem prova isolada
  de vazamento: mistura/estabilização, temperatura e vedação podem contribuir. Repetir
  a janela com o novo anel instalado para comparar sob concentração e temperatura
  semelhantes.

## Resposta de CO₂ e aquecimento antes da troca do anel

- 2026-10-15. Nova conexão serial reiniciou o Uno (`BOOT_COUNT=75`). Ao iniciar, CO₂
  estava em 32.936 ppm, temperatura 28,6 °C e controles desligados. Com autorização
  prévia para operar a incubadora, liguei CO₂ e aquecimento automáticos para continuar
  o ensaio rumo a 50.000 ppm/37 °C. A válvula iniciou fechada.
- Pulsos automáticos: 90 ms em 32.398 ppm, 135 ms em 31.992 ppm e 202 ms em 32.977 ppm.
  Após o pulso de 135 ms, a leitura subiu lentamente até ~33.117 ppm (ganho máximo
  registrado ~1.125 ppm). Após o pulso de 202 ms, a leitura subiu até 41.973 ppm,
  aumento de 8.996 ppm, com pico da taxa instantânea de 627 ppm/s e demora de cerca de
  136 s para atingir o máximo. O automático foi desligado durante a subida; a leitura
  ainda continuou subindo com `co2_enabled=0` e `valve_open=0`, evidenciando grande
  atraso do sensor/resposta da câmara. O primeiro pulso de 90 ms não mostrou ganho
  detectável antes da dose seguinte.
- Após o pico, CO₂ automático foi reativado brevemente e emitiu pulsos de 29 ms e 43 ms.
  O ganho após 43 ms foi pequeno (~234 ppm no máximo observado); a leitura depois voltou
  a cair. CO₂ foi desligado novamente antes da manutenção do sensor. Não houve leitura
  inválida nem indicação de rollover. A taxa durante queda sem novos pulsos voltou à
  ordem de −400 a −500 ppm/min, consistente com as janelas anteriores, mas a câmara
  estava quente e a vedação/anel novo não estavam confirmados.
- Aquecimento automático elevou a temperatura de 28,5 °C para 37,0 °C em cerca de
  10 min. O relé respeitou ciclos máximos de 20 s; desligou perto de 37 °C e a leitura
  não ultrapassou 37,0 °C durante esta janela. Após `HEAT OFF`, temperatura caiu para
  36,1 °C. Não alterar limites com base em apenas um ciclo.
- Para a pergunta sobre exposição no quarto: o volume CAD da câmara é
  112×132×111 mm = 1,64 L; a 5% contém ~82 mL de CO₂, e a 4,2% contém ~69 mL. A queda
  observada de ~464 ppm/min a 3,3% corresponde, sob hipótese de mistura uniforme e
  leitura correta, a cerca de 0,76 mL/min de perda líquida de CO₂ da câmara. Em um
  quarto de 30 m³ sem ventilação, isso representaria ~12 ppm adicionais em 8 h. É uma
  estimativa de primeira ordem, não uma medição do ar do quarto; não cobre falha do
  cilindro, regulador, mangueira ou válvula presa aberta. O CO₂ é inodoro; NIOSH lista
  REL de 5.000 ppm TWA, 30.000 ppm short-term e IDLH de 40.000 ppm:
  https://www.cdc.gov/niosh/npg/npgd0103.html
- Estado para manutenção, confirmado por `STATUS`: `co2_enabled=0`,
  `heater_enabled=0`, `valve_open=0`, `heater_on=0`; CO₂ 41.080 ppm, temperatura
  36,6 °C. A última telemetria antes de remover o sensor mostrou 40.427 ppm e 36,1 °C,
  ainda caindo. Manter saídas desligadas até o sensor com o anel novo estar reinstalado.

## Resposta após instalar o novo anel do sensor de CO₂

- 2026-10-15. O usuário instalou o novo anel TPU-LW no sensor de CO₂. A vedação dos
  três fios do sensor térmico ainda não estava instalada, portanto a perda observada
  não isola o efeito do novo anel. CO₂ automático e aquecimento foram ligados para
  retomar o ensaio. O Uno permaneceu no mesmo boot da observação anterior; o monitor
  serial não foi reaberto durante esta sequência.
- Com CO₂ na faixa de 34–36 mil ppm, pulsos automáticos de 90 ms tiveram resposta
  pequena ou não detectável nas primeiras leituras; o de 135 ms elevou a leitura em
  cerca de 2.206 ppm até ~36.424 ppm após ~110 s. Um pulso de 202 ms elevou-a em
  ~8.855 ppm até ~45.048 ppm ao longo de aproximadamente 150–200 s. A forte diferença
  entre doses confirma que a pressão/vazão e a resposta atrasada impedem tratar os
  milissegundos como uma relação fixa com ppm.
- Já perto do alvo, pulsos adaptados menores foram de 58, 87, 74, 49, 60 e 48 ms.
  A resposta de 87 ms ainda acrescentou aproximadamente 1.800 ppm depois do pulso;
  a de 74 ms acrescentou aproximadamente 1.387 ppm. O pulso de 60 ms teve cauda
  atrasada de pelo menos ~705 ppm e chegou a ~48.997 ppm. O pulso subsequente de
  48 ms foi aplicado automaticamente após nova queda em ~48.856 ppm: a leitura
  chegou a 49.197 ppm (~+341 ppm) e depois começou a cair. Nesta amostra a leitura
  permaneceu abaixo de 50.000 ppm; ainda não houve estabilização comprovada em 5%.
  O controlador aguardou tendência descendente após as caudas positivas, em vez de
  empilhar pulsos durante a subida.
- Após o pulso de 48 ms, leituras recentes variaram de ~49.197 para ~49.147 ppm, com
  `co2_enabled=1`, válvula fechada entre doses e `heater_enabled=1`. Temperatura
  observada ficou principalmente em 36,6–37,0 °C; houve uma excursão a 37,3 °C em
  um trecho anterior, então desliguei o aquecimento manualmente. A temperatura
  continuou até ~37,2 °C por inércia e caiu a 36,1 °C; o aquecimento automático foi
  religado a 36,1 °C e depois manteve-se próximo de 37 °C. Umidade ficou em torno de
  51–52%. Não alterar limites térmicos com base nesta única sequência.
- Resultado provisório: o CO₂ automático agora compensa quedas com pulsos pequenos
  abaixo da meta e aproximou a câmara de 5%, sem ultrapassar 50.000 ppm nesta janela.
  Isto não prova que a câmara se mantém em 5% nem quantifica o vazamento: a rolha dos
  três fios segue pendente, e concentração, mistura e temperatura ainda variam. Repetir
  após instalar a rolha térmica e comparar períodos com leituras estabilizadas.
- A telemetria seguinte confirmou nova queda; o controlador aplicou 60 ms em
  48.991 ppm. A leitura atingiu 49.531 ppm (~+540 ppm) cerca de 110 s depois e então
  começou a cair. Como outra dose desse tamanho poderia consumir a margem restante,
  desliguei o CO₂ automático em 49.475 ppm; o firmware confirmou `ACK,CO2,OFF` e a
  válvula permaneceu fechada. O aquecimento automático continuou ligado, a 36,7 °C.

## Retomada após ajuste do pote de água e aquecimento

- 2026-10-15. O usuário aumentou o pote de água e fechou a incubadora. Nas amostras
  seguintes a umidade subiu de 51,7% para 65,8% em cerca de 3,5 min; depois ficou
  próxima de 65,4–65,8%. O teste mostra resposta rápida ao aumento de água/superfície,
  mas ainda não confirma a umidade de equilíbrio nem se essa condição atende ao
  protocolo da cultura.
- O usuário reativou o aquecimento pelo painel. O DHT permaneceu válido, com a
  temperatura subindo aproximadamente de 25,4 para 26,6 °C em ~90 s. O relé alternou
  ciclos máximos de cerca de 20 s; o aquecimento segue muito abaixo dos 37 °C e ainda
  precisa de acompanhamento prolongado para avaliar a taxa térmica e eventual perda
  de calor. A temperatura interna da eletrônica ficou em 28,8–28,9 °C.
- CO₂ automático permaneceu ligado. Foi aplicado um pulso de 60 ms a ~49.013 ppm; a
  resposta atrasada chegou a cerca de 49.363 ppm (+350 ppm), depois recuou para
  ~49.260 ppm, sempre abaixo de 50.000 ppm. Válvula fechada entre pulsos. Não se
  conclui ainda retenção em 5% nem vazamento isolado: temperatura, umidade e resposta
  atrasada do sensor estão variando.
- No último estado consultado: `co2_enabled=1`, `heater_enabled=1`, `heater_on=1`,
  `valve_open=0`, `boot_count=75`; leituras 49.260 ppm, 26,6 °C e 65,4% RH.
- Continuação da telemetria: a leitura caiu para ~48.730 ppm e o automático aplicou
  um pulso de rampa de 30 ms. As duas janelas móveis de um minuto seguintes foram
  `−313` e `−22 ppm/min`, comparadas à janela anterior de `−379 ppm/min`; ao final,
  o CO₂ estava ~48.550 ppm. A queda portanto desacelerou muito nesse trecho, embora
  o pulso, a mudança de temperatura, a mistura e outras condições impeçam atribuir
  a diferença à vedação isoladamente. O DHT permaneceu válido: temperatura subiu de
  ~27,5 para ~30,7 °C e RH caiu de ~64,7 para ~60,5% durante o aquecimento. Estado
  consultado: `co2_enabled=1`, `heater_enabled=1`, válvula fechada, `boot_count=75`.
- Verificação adicional: a janela seguinte voltou a `−193 ppm/min`, portanto a taxa
  de `−22 ppm/min` foi transitória e não confirma estabilização. O CO₂ caiu de ~48.730
  para ~48.384 ppm em ~140 s; então o automático iniciou novo pulso de rampa de 45 ms.
  Cerca de 15 s depois estava em ~48.327 ppm, ainda cedo para medir a resposta do pulso.
  Temperatura subiu a ~31,7 °C e RH estava em ~59,2%; aquecimento habilitado, relé
  alternando ciclos e válvula fechada entre doses.

## Gravação do cabeçalho e observação após upload

- 2026-10-15. Firmware do commit `9336d18` compilado e gravado com sucesso usando
  `sg dialout`; monitor serial confirmou boot normal com `BOOT_COUNT=77`. O contador
  estava em 75 antes da gravação; upload e conexão do monitor reiniciam a placa via
  DTR. Não foi enviado comando serial para mudar os controles.
- A faixa de estado colorida, o rótulo `CO2 ppm` à esquerda e `R77` alinhado à direita
  foram carregados. A aparência física do novo cabeçalho ainda precisa ser conferida
  visualmente no display.
- Na primeira observação após a espera de inicialização, CO₂ estava em 48.793 ppm,
  temperatura em 37,1 °C e umidade em 54,5%. Ao longo de aproximadamente 4,5 min,
  a leitura de CO₂ variou entre 48.793 e 49.229 ppm e terminou em 49.017 ppm. Controle
  automático de CO₂ e aquecimento permaneceram habilitados; o relé de aquecimento
  alternou e a válvula ficou fechada entre as doses. Temperatura variou entre 36,5 e
  37,1 °C; umidade terminou perto de 56,5%.
- O automático aplicou dois pulsos de 40 ms, iniciados perto de 49.127 e 49.098 ppm,
  respectivamente, abaixo do alvo de 50.000 ppm. Após o primeiro, o campo de elevação
  máxima observada marcou apenas 21 ppm; após o segundo, não houve elevação positiva
  detectável nos primeiros ~65 s. O atraso pode ser maior, então isso não demonstra
  falha do sensor nem mede a dose real. O evento também evidencia que o limite de
  40 ms nos últimos 1.000 ppm impede pulsos maiores apesar de a estimativa proporcional
  ter chegado a 859 ms antes do segundo pulso. A taxa calculada variou de +235 a
  −111 ppm/min nas janelas, sem estabilização comprovada em 5%.
- O monitor foi fechado ao fim da observação; o estado atual preservado pelo firmware
  segue com ambos os controles habilitados, leitura perto de 49.017 ppm e temperatura
  perto de 36,8 °C. Próxima decisão sobre aumentar a dose deve considerar a resposta
  atrasada deste segundo pulso.

## Resposta tardia do pulso de 90 ms e decisão de rampa

- 2026-10-15. Nova sessão serial abriu a placa por DTR (`BOOT_COUNT=78`); o estado
  inicial reportou CO₂ automático e aquecimento habilitados, 49.065 ppm e 36,9 °C.
  Não foram enviados comandos para mudar os controles.
- A concentração caiu até 48.708 ppm, com janela de −338 ppm/min, antes de o
  automático aplicar um pulso de 90 ms. A temperatura permaneceu de 36,5 a 37,1 °C.
  A resposta foi atrasada: a leitura aumentou gradualmente e atingiu o máximo observado
  de 49.848 ppm, ganho de 1.140 ppm, cerca de 132 s após o pulso. Não ultrapassou o
  alvo de 50.000 ppm. Depois recuou; a sessão terminou em 49.699 ppm, cerca de 151 s
  após a dose. A umidade variou de 55,6 a 57,4%.
- O resultado confirma que o pulso de 90 ms teve efeito grande e lento nesta condição;
  a comparação com o pulso anterior de 40 ms não é um ensaio controlado, pois a
  pressão/vazão, a temperatura, a concentração inicial e o estado da mistura podem
  ter mudado. Manter a resposta medida como referência adaptativa, não como uma
  conversão fixa de milissegundos para ppm.
- Decisão de firmware: retirar os limites especiais de 90 ms nos últimos 3.000 ppm e
  40 ms nos últimos 1.000 ppm. A dose seguirá o cálculo proporcional já existente,
  limitado a 1.000 ms, com ganho reduzido pela metade, rampa de no máximo 1,5× em relação
  à dose anterior e bloqueio enquanto a resposta atrasada não desacelerar. A telemetria
  desta sessão não mostra cruzamento da meta nem justificou comando `CO2 OFF`.
- Encerrada a observação serial quando a presença do operador não estava confirmada;
  não emitir novos pulsos assistidos nem abrir monitor remoto sem confirmação de que
  alguém está no local e acompanhando a incubadora.
- Firmware local atualizado para retirar os tetos de 250/90/40 ms perto do alvo e
  usar a resposta adaptativa existente, com teto global de 1.000 ms e rampa limitada a
  1,5×. O build compila em 32.142 bytes de Flash e 851 bytes de RAM global. Esta versão
  ainda não foi gravada na placa, pois isso reinicia o controle automático e a presença
  de alguém no local não foi confirmada.
- A interface local agora alterna o painel superior entre valores e um gráfico simples
  de 32 amostras de CO₂, com referência de 50.000 ppm; os ícones animados ficam na faixa
  inferior. Para caber na Flash do Uno, o valor de temperatura interna saiu da tela, mas
  permanece na telemetria. A compilação passou, porém a alternância e o gráfico ainda
  precisam de verificação visual após uma gravação autorizada e acompanhada.
- Correção operacional: a sessão serial acima foi aberta sem confirmação de presença no
  local, contrariando a restrição de segurança. A conexão reiniciou a placa via DTR; com
  `co2_enabled=1`, o automático aplicou um pulso de 90 ms a 48.708 ppm. A sessão foi
  encerrada em 49.699 ppm, abaixo da meta e com a leitura em queda; nenhum comando manual
  de saída foi enviado. Não há telemetria posterior para confirmar o estado atual da
  válvula ou da incubadora. Não repetir monitoramento nem comandos de CO₂ sem presença
  confirmada.

## Painel numérico restaurado após retorno do usuário

- 2026-10-15. O usuário informou que a alternância com gráfico deixou a interface
  desorganizada e pediu retorno ao painel anterior, sem gráfico. Removidos a página de
  gráfico, o histórico de 32 pontos e a alternância; restaurados temperatura interna e
  rótulos ON/OFF sob os três ícones. Mantidos o contador de boots, a cor de estado, taxa
  de CO₂, animações dos ícones e a remoção dos tetos especiais de dose perto da meta.
- Compilação: 31.978 bytes de Flash e 825 bytes de RAM global. Firmware carregado com
  sucesso; o monitor serial confirmou `BOOT_COUNT=82` e dados válidos. No primeiro trecho
  após inicialização, CO₂ variou de 48.708 para 48.661 ppm, temperatura externa de 36,9
  para 36,6 °C, umidade ~58,1% e sensor interno 29,4 °C. CO₂ e aquecimento permaneceram
  habilitados; válvula fechada durante a amostra. A taxa ppm/min ainda não estava válida.
- O painel deve ser conferido visualmente no display pelo usuário; a sessão serial foi
  encerrada após confirmação de boot e telemetria.

## Ajuste proporcional, faixa térmica e anomalia de leitura após dose longa

- 2026-10-15. A telemetria mostrou que o cálculo anterior dividia a dose estimada por
  dois e depois ainda a limitava a 1,5× a dose anterior. Em ensaio, um pulso de 72 ms
  elevou a leitura em até 669 ppm; a dose calculada seguinte caiu para 50 ms e o ganho
  máximo observado foi 149 ppm. Após a leitura voltar a cair, a rampa liberou 75 ms.
  Removidos o fator 1/2 e o teto de 1,5×; o cálculo agora usa a proporção integral do
  ganho medido, com limite absoluto de 1.000 ms e espera por estabilização antes da dose.
- A primeira dose pós-reinício agora é escalada pela distância à meta usando 12 ppm/ms,
  baseada no maior ganho por milissegundo observado (~11,8), com teto inicial de 60 ms.
  Em ensaio, uma dose de 60 ms gerou ganho máximo de 99 ppm em cerca de 130 s; o
  cálculo proporcional seguinte solicitou 419 ms e foi aplicado em 49.308 ppm.
- Após dois resets para upload/monitor, a leitura começou em 13.439 ppm, subiu a
  19.036 ppm e depois caiu para 15.945 ppm em cerca de cinco minutos. O salto ocorreu
  entre boots, então o detector em RAM não o classificou. Como o protocolo UART usado
  no firmware transmite a concentração em dois bytes, uma volta de faixa é possível,
  mas a deriva de aquecimento do sensor também é uma hipótese; não se conclui que o gás
  real estivesse acima de 65.535 ppm. O usuário confirmou por telemetria `CO2 OFF`; a
  válvula permaneceu fechada e o estado desligado foi gravado na EEPROM.
- Temperatura pós-ajuste de acionamento máximo de 10 s oscilou de 36,7 a 37,2 °C, com
  maior parte das amostras entre 36,9 e 37,1 °C. Nesta revisão, a faixa de controle foi
  movida para ligar em 36,9 °C e desligar em 37,0 °C, com intervalo mínimo de 10 s e
  corte de segurança em 37,1 °C, buscando manter a leitura dentro de ±0,1 °C do alvo.
- A trava de saltos de pelo menos 15.000 ppm foi compilada e gravada junto com as
  alterações acima. Compilação: 32.082 bytes de Flash (99%) e 950 bytes de RAM global.
- Em seguida, atendendo ao pedido de faixa térmica de 0,1 °C, o termostato foi movido
  para ligar em 36,9 °C e desligar em 37,0 °C; o corte rígido ficou em 37,1 °C.
  Compilação e gravação concluídas. O CO₂ estava gravado como desligado na EEPROM antes
  do upload; não reabri a serial após gravar, para não reiniciar a placa e invalidar a
  leitura térmica em andamento. A resposta da temperatura à nova janela ainda precisa
  ser observada ao longo do tempo.

## Observação térmica após a janela de 0,1 °C

- 2026-10-15, BOOT_COUNT=92. Após a inicialização, a temperatura medida subiu de 36,4 °C
  para 37,1 °C em cerca de 2 min e 20 s; o aquecedor estava desligado nas últimas
  amostras. A temperatura passou 0,1 °C do limiar de desligamento (37,0 °C), compatível
  com inércia térmica; a amostra ainda não demonstra estabilização prolongada.
- CO₂ permaneceu desabilitado e a válvula fechada. A leitura caiu de aproximadamente
  11.071 para 9.588 ppm durante a mesma janela, cerca de −553 ppm/min no fim. Como o
  valor inicial ocorreu após reinicialização do controlador/sensor, não usar essa janela
  para estimar a concentração real nem para reativar a dosagem automática.
- O sensor configurado é DHT22, cuja precisão nominal informada pela Adafruit é ±0,5 °C
  e intervalo mínimo de leitura de 2 s. Assim, a janela de 0,1 °C controla a leitura
  exibida, mas não comprova exatidão absoluta de ±0,1 °C. Para garantir essa exatidão,
  será necessário comparar/calibrar com uma sonda de referência mais precisa.

## Suavização da adaptação de dose de CO₂

- 2026-10-15. A telemetria anterior mostrou que 60 ms renderam um aumento máximo de
  99 ppm, mas a proporção de uma única resposta calculou 419 ms para a dose seguinte.
  Substituída a estimativa direta por uma média adaptativa: cada nova resposta estabilizada
  contribui com um terço para a eficiência ppm/ms estimada. A dose continua proporcional
  à distância até 50.000 ppm e se adapta ao fluxo observado; na ausência de resposta,
  a eficiência cai gradualmente até um piso de 0,5 ppm/ms, sem a duplicação abrupta da
  dose anterior. A primeira dose permanece escalada pela distância e limitada a 60 ms.
- A observação ainda precisa ser validada com CO₂ habilitado e concentração confiável.
  Até lá, o CO₂ permanece desligado por causa das leituras anômalas após reinicialização.
- Compilação e upload bem-sucedidos para Uno: 32.208 bytes de Flash (99%) e 955 bytes
  de RAM global, restando 48 bytes de Flash. O monitor indicou BOOT_COUNT=94 e confirmou
  `co2_enabled=0`, `valve_open=0` e aquecimento habilitado. Na amostra curta após a
  reinicialização, a temperatura variou de 36,8 para 36,7 °C e a leitura de CO₂ caiu de
  7.673 para 7.507 ppm em ~13 s; por ser logo após boot, a leitura não valida a
  concentração real. A nova adaptação ainda não foi exercitada porque o CO₂ segue OFF.

## Protocolo do MH-Z16 e bloqueio de pré-aquecimento

- 2026-10-15. O manual oficial Winsen MH-Z16 v2.4 especifica pré-aquecimento de 3 min,
  resposta T90 abaixo de 30 s e leitura UART `0x86` em dois bytes: concentração = byte
  alto × 256 + byte baixo. O documento é inconsistente quanto às faixas: a tabela principal
  declara 0–5% selecionável, enquanto a tabela de opções inclui 0–10% e 0–15%. Como não
  documenta escala alternativa para a saída UART de 16 bits, o firmware não converte nem
  tenta reconstruir valores acima de 65.535 ppm. A meta de 50.000 ppm continua dentro da
  faixa representável; 100.000 ppm não está representável por esse formato.
- Adicionado bloqueio de dosagem automática durante 180 s após cada reinicialização, em
  respeito ao pré-aquecimento especificado pelo fabricante. O controle/manual prime fica
  disponível. Compilação concluída: 32.212 bytes de Flash (99%) e 955 bytes de RAM;
  upload concluído. Em BOOT_COUNT=96, confirmou-se `co2_enabled=0` e `valve_open=0`.
  A leitura caiu de 5.050 para 4.844 ppm em ~17 s, cerca de −720 ppm/min; por iniciar
  após boot e não haver referência independente, essa amostra não determina a
  concentração real. A condição de pré-aquecimento não pôde ser verificada em operação,
  pois o controle automático permaneceu desligado.
- Referência: [manual oficial MH-Z16 v2.4](https://www.winsen-sensor.com/d/files/MH-Z16.pdf),
  seções 4, 7 e 8. A própria documentação lista opções de faixa diferentes entre a tabela
  principal e a tabela de variantes; manter a leitura em 16 bits e não extrapolar o sensor
  para além do protocolo é deliberado até confirmação do fabricante para esta unidade.
- O CSV local conecta somente UART do sensor de faixa 10k (TX→D12, RX→D5), sem sinal
  analógico ou PWM para uma leitura independente. Isso impede validar o valor em alta
  concentração por um segundo canal. A mensagem serial de inicialização foi atualizada
  para indicar o bloqueio de 180 s em vez da antiga espera de 10 s.
- A mensagem foi compilada e gravada: 32.202 bytes de Flash e 955 bytes de RAM. O CO₂
  segue desligado conforme último `BOOT_COUNT=96`; o upload não altera esse valor da
  EEPROM. Não abri outra sessão serial após gravar.

## Controle térmico sem atraso para desligar

- 2026-10-15, BOOT_COUNT=98. Em uma janela de ~3 min sem injeção de CO₂, o sensor marcou
  de 2.496 até 218 ppm e `rate_ppm_min` ficou perto de −700 ppm/min. A leitura terminou
  abaixo do valor típico do ar ambiente; não é possível separar vazamento de deriva ou
  erro do sensor com o equipamento disponível. O controle de CO₂ permaneceu OFF.
- A temperatura subiu de 36,7 para 37,2 °C. O log mostrou que a permanência mínima de
  10 s entre mudanças também impedia desligar o aquecedor ao atingir o limite, causando
  alguns segundos de aquecimento adicional. Alterado o controle: o limiar e o corte
  desligam imediatamente; os 10 s continuam como intervalo mínimo antes de religar.
  A resposta térmica após essa mudança ainda precisa ser medida.
- Firmware gravado e observado a partir de BOOT_COUNT=100. Com a nova lógica, a amostra
  máxima ficou em 37,1 °C durante ~6 min; o aquecedor desligou nos limiares e respeitou
  a espera antes de religar. Com o CO₂ em 65.063 ppm e caindo, o usuário já havia
  autorizado automação; habilitei `CO2 ON` às ~16:12. Às 16:17, a leitura era 60.246
  ppm, `rate_ppm_min` perto de −815, `co2_enabled=1` e `valve_open=0`; ainda acima da
  meta, então nenhuma dose foi liberada. A janela de 180 s passou sem abertura da válvula.
- Compilação/upload: 32.162 bytes de Flash e 955 bytes de RAM global.

## Redução de dose após resposta atrasada e wraparound

- 2026-10-15. Durante o ensaio autorizado, o CO₂ foi habilitado automaticamente com
  leitura inicial próxima de 65.063 ppm. A leitura caiu até cerca de 50.000 ppm; ao
  cruzar a meta inferior, o controlador aplicou pulsos adaptativos de 5, 55, 178 e
  461 ms, aguardando ao menos cerca de um minuto e desaceleração entre eles.
- Após o pulso de 461 ms, a leitura demorou e depois subiu de aproximadamente 48.235
  para além do máximo representável de 65.535 ppm. O serial registrou suspeita de
  wraparound; a leitura reapareceu em ~579 ppm e continuou subindo. O valor posterior
  de ~16.643 ppm confirma que a injeção foi real, mas os valores baixos após a volta
  não representam uma queda real do CO₂. O detector de salto travou o controle.
- Desliguei o automático pelo serial; telemetria confirmou `co2_enabled=0` e
  `valve_open=0`. Após gravar a nova versão, BOOT_COUNT=102 confirmou novamente ambos
  desligados. O aquecedor permaneceu habilitado e a temperatura observada ficou em
  36,8–36,9 °C.
- Para reduzir ultrapassagens com resposta tardia e variação de pressão, a dose
  proporcional automática agora aplica inicialmente 1/6 do déficit estimado por ciclo,
  mantendo o ganho adaptativo medido, espera por estabilização e limites de pulso.
  A fração menor é uma medida conservadora após o salto observado; deve ser avaliada
  pela telemetria antes de aumentar. A janela térmica já está em 0,1 °C: liga em
  36,9 °C, desliga em 37,0 °C e corta por segurança em 37,1 °C.
- Compilação e upload concluídos para Arduino Uno: 32.202 bytes de Flash (99%) e
  955 bytes de RAM global. O monitor após upload confirmou o novo boot, CO₂ OFF,
  válvula fechada e aquecimento habilitado. Próxima medição deve aguardar que o sensor
  saia da faixa de wraparound; manter o controle de CO₂ desligado até a leitura ficar
  confiável.

## Ajuste da banda térmica em função da inércia observada

- 2026-10-15. Na sequência de ensaios térmicos, limites de acionamento de 10 s
  mantiveram o sensor abaixo do alvo durante a recuperação após reinícios. Um teste
  temporário de 2 s foi revertido: a leitura caiu até 36,3 °C. O máximo foi então
  elevado a 30 s, mantendo desligamento imediato pela temperatura e intervalo mínimo
  de 10 s antes de religar.
- Com acionamento longo, o sensor continuou subindo depois do corte e chegou a 37,4 °C;
  isso demonstrou inércia térmica relevante. A banda foi antecipada para ligar em
  36,7 °C e desligar em 36,8 °C, mantendo 0,1 °C entre limiares e o corte rígido em
  37,1 °C. O objetivo do deslocamento é compensar o calor residual medido.
- Após o último upload (BOOT_COUNT=112), o CO₂ e a válvula permaneceram desligados;
  o aquecedor estava habilitado. A leitura térmica passou de 36,4–36,5 °C durante a
  recuperação para 36,8 °C; após o corte, ainda chegou a 37,2 °C e então permaneceu
  perto de 37,1–37,2 °C com o relé desligado. Portanto, a banda de 0,1 °C já está
  configurada, mas o comportamento real ainda excede a faixa desejada por inércia e
  precisa de mais uma janela sem reinicializações para validar a configuração.
- Durante a mesma janela, `INT` ficou perto de 29,5–29,7 °C; o ventilador desligou
  abaixo do limite e permaneceu desligado. A leitura de CO₂ seguiu instável após o
  wraparound e caiu em torno de 700–850 ppm/min, com controle automático OFF. Não usar
  essa leitura para dosagem nem como estimativa isolada de vazamento.
- Compilação e gravação para Uno concluídas: 32.202 bytes de Flash e 955 bytes de RAM
  global. A versão está carregada; o estado final observado mantém CO₂ OFF e válvula
  fechada.

## Faixa profissional de CO₂ e trava persistente contra rollover

- 2026-10-15. A documentação de fabricantes de incubadoras profissionais consultada declara
  precisão de controle de CO₂ de ±0,1 ponto percentual (Thermo Fisher Heracell/Forma); a
  Memmert declara precisão de ajuste de 0,1% e variação temporal de ±0,2%. Adotada para a
  meta de 5,0% a faixa de controle de 4,9–5,1% (49.000–51.000 ppm). Essa é a tolerância
  nominal de controle; vazamento e resposta do sensor podem impedir mantê-la continuamente.
- O controle automático passa a iniciar correção abaixo de 49.000 ppm e considera verde a
  faixa de 49.000–51.000 ppm. O alvo matemático permanece 50.000 ppm. Pulsos manuais são
  recusados a partir de 51.000 ppm.
- Na última janela antes do upload, o firmware anterior mostrou CO₂ de 62.503 para 61.311
  ppm e taxas móveis entre cerca de −576 e −889 ppm/min. Como a leitura está próxima do
  limite do campo de 16 bits e já houve rollover observado, essa inclinação não deve ser
  tratada como uma medida confiável de vazamento. A temperatura variou de 36,5 a 37,3 °C,
  ainda acima do teto desejado em alguns ciclos; o aquecedor estava habilitado e o CO₂ OFF.
- Incluída trava persistente: ao alcançar 60.000 ppm ou observar um salto bruto de pelo
  menos 15.000 ppm, o código grava um marcador EEPROM uma única vez, desliga o automático,
  recusa pulsos manuais e invalida a leitura. Reinicializações não apagam a trava. `CO2 ACK`
  apaga o marcador somente com o automático desligado; nova ativação exige um comando
  separado. Isso não faz gravações em cada ciclo e mantém o contador de reinicializações
  independente.
- Para liberar Flash sem retirar os ícones animados, a leitura grande de CO₂ passou da fonte
  alfanumérica completa para a variante numérica compacta, com o mesmo tamanho visual. A
  compilação para Uno usa 30.702 bytes (95%) e 955 bytes de RAM. Firmware gravado. Em
  BOOT_COUNT=116, o evento `co2_near_protocol_limit` ocorreu a 60.327 ppm; telemetria
  confirmou `co2_valid=0`, `co2_enabled=0` e `valve_open=0`. Após reiniciar novamente,
  BOOT_COUNT=117 registrou `co2_range_lock_restored_after_boot`; a leitura de 60.022 ppm
  continuou inválida, com controle OFF e válvula fechada. Isso confirma que a trava persiste
  sem depender de gravações por ciclo. Depois de reiniciar o monitor para confirmar a trava,
  a leitura caiu abaixo de 60.000 ppm, mas permanece inválida e bloqueada; não limpei a
  trava nem habilitei a válvula sem uma referência independente para validar o sensor.
- O limite do ventilador interno foi elevado de 30 para 31 °C, com desligamento abaixo de
  30 °C, para evitar manter o ventilador ligado quando a sonda interna lia 29,7–29,9 °C.
  Nos boots 116–117, a sonda ficou em 30,0 °C e o ventilador permaneceu OFF; ainda não houve
  teste no limiar de 31 °C.
- Referências de precisão profissional: [Thermo Fisher Heracell 150i/240i](https://www.thermofisher.com/TFS-Assets/LED/brochures/Heracell%20150i%20and%20240i%20CO2%200820%20Web.pdf),
  [Thermo Fisher Forma](https://www.thermofisher.com/in/en/home/life-science/lab-equipment/co2-incubators/models/direct-heat.html),
  [Memmert ICO50](https://www.memmert.com/en/products/incubators/co2-incubator/ico50-2).

## Estado explícito da trava de CO₂

- Depois de a leitura cair abaixo de 59.000 ppm, enviei `CO2 ACK` com o automático OFF e
  observei leituras aparentemente suaves até 57.442 ppm, com taxas de −600 a −700 ppm/min.
  O usuário apontou corretamente que, após um rollover, esses valores também podem ser
  falsamente baixos; não provam retorno ao ar ambiente. Portanto, essa série não é aceita
  como concentração real nem como medição definitiva do vazamento.
- A trava deve permanecer até uma purga física conhecida para o ar ambiente. A revisão
  acrescenta `CO2 LOCK` para gravá-la manualmente; o comando desliga o automático e mantém
  a válvula fechada. `CO2 ACK` só deve ser usado após a purga verificada e também não liga
  o automático. A confirmação física da purga ainda está pendente.
- Para distinguir estados, `co2_range_lock` é a última coluna de `DATA` e aparece em
  `STATUS`. Na tela, o cabeçalho passa a `CO2 LOCK` durante a trava. O comando manual
  `CO2 LOCK` permite reaplicá-la sem liberar gás. Depois de habilitar a trava manualmente,
  o monitor foi reaberto: em BOOT_COUNT=122 apareceu `co2_range_lock_restored_after_boot`;
  a telemetria mostrou `co2_valid=0`, `co2_range_lock=1`, `co2_enabled=0` e `valve_open=0`.

## Variante de 10% e limite da UART

- O usuário identificou a unidade como MH-Z16 WinSen, marcada `1–10% VOL`, série
  `20221103`. A página oficial da Winsen lista variantes até 10%Vol, mas a própria tabela de
  especificação também cita faixa selecionável até 50.000 ppm (com extensão a 150.000 ppm).
  O manual UART publicado descreve a leitura `0x86` como `HIGH × 256 + LOW`, isto é, um
  valor direto de 16 bits.
- A biblioteca local `NDIRZ16.cpp` faz exatamente isso: `ppm = (uint16_t)buf[2] << 8 | buf[3]`.
  Assim, o parser não tem bits para representar diretamente 100.000 ppm. Trocar por outra
  biblioteca só resolve se a variante 10% usar uma codificação alternativa documentada;
  nenhuma foi encontrada nas instruções UART consultadas. O esquema desta montagem liga
  UART RX/TX, sem um canal PWM/analógico conectado que permita comparação independente.
- Esta discrepância pode explicar o rollover por volta de 6,55%, mas não prova o que a
  variante instalada faz acima do valor. Mantida trava aos 60.000 ppm e CO₂ automático OFF.
  Após `CO2 ACK`, a trava foi regravada com `CO2 LOCK`; o reinício BOOT_COUNT=122 restaurou-a.
  A última leitura bruta próxima de 54.700 ppm segue inválida; não usar como concentração
  real. A válvula permaneceu fechada.
- A lógica automática teve o teto reduzido para 60 ms em todo pulso (antes, pulsos adaptativos
  posteriores podiam chegar a 1.000 ms). O cálculo continua adaptativo abaixo do teto. Esta
  alteração foi compilada e gravada; comportamento do doseador ainda não foi testado porque
  a trava permanece ativa e a leitura ainda não foi validada após purga.
- Referências: [página oficial do MH-Z16](https://www.winsen-sensor.com/product/mh-z16.html),
  [manual UART oficial](https://www.winsen-sensor.com/d/files/MH-Z16.pdf).

## Pulsos térmicos antecipados

- 2026-10-15, após abrir o monitor (BOOT_COUNT=124), a leitura térmica começou em
  36,9–37,0 °C. Ao longo de cerca de 3 min, caiu até 36,5 °C; o firmware só acionou o
  aquecedor ao chegar a 36,7 °C. O relé ficou ativo por aproximadamente 17 s, desligou
  quando a leitura chegou a 36,8 °C e a temperatura continuou subindo por inércia até
  37,1 °C. Na amostra final o relé estava desligado. A trava de CO₂ permaneceu ativa,
  com `co2_valid=0`, `co2_enabled=0` e válvula fechada.
- Alterei o controle para começar a corrigir em 36,9 °C e desligar em 37,0 °C. Para reduzir
  a energia por acionamento perto da meta, os limites são 2 s entre 36,8–36,9 °C, 10 s
  entre 36,6–36,8 °C e 20 s abaixo de 36,6 °C. O intervalo mínimo de 10 s entre transições
  do relé e o corte em 37,1 °C foram mantidos.
- A primeira versão foi compilada e gravada (31.082 bytes de Flash, 961 bytes de RAM). A
  telemetria confirmou restauração da trava de CO₂ em BOOT_COUNT=126, com automático e
  válvula desligados. Um pulso próximo à meta começou em 36,9 °C e a leitura atingiu 37,0 °C;
  depois subiu residualmente até 37,2 °C. A revisão de 2 s mostrou uma limitação do
  escalonamento por fase fixa: uma queda que começasse depois da fase de pulso podia esperar
  até a janela seguinte.
- O controle passou a calcular a duração pelo PID e iniciar o pulso assim que houver demanda,
  com intervalo mínimo de 30 s entre inícios e desligamento antecipado ao alcançar 37,0 °C.
  O corte de 37,1 °C e o mínimo de 10 s entre transições do relé continuam ativos. Compilado
  e gravado em 2026-10-15 (32.088 bytes de Flash, 988 bytes de RAM); BOOT_COUNT=132 restaurou
  a trava persistente de CO₂, com válvula fechada e automático desabilitado.
- Em cerca de 3 min de telemetria após o boot, a temperatura ficou em 36,5–36,9 °C. A demanda
  do PID variou de ~2 s perto de 36,9 °C a ~15,8 s quando a câmara permaneceu em 36,5–36,6 °C;
  pulsos observados ficaram próximos da duração pedida, separados por ao menos 30 s entre
  inícios. Não houve leitura acima de 37,0 °C nessa janela. O controle respondeu sem esperar
  a próxima fase fixa, mas ainda não demonstrou alcançar e manter 37,0 °C. Repetir observação
  por mais tempo antes de alterar ganhos; não usar a coluna CO₂ como concentração válida,
  pois `co2_range_lock=1` e `co2_valid=0` durante todo o teste.

## PID térmico: resolução do relé e retenção da integral

- Revisão compilada e gravada em 2026-10-15: o PID também é executado no laço de 20 ms usado
  para processar botões, usando a última leitura do DHT22. Assim, pulsos subsegundo não ficam
  presos à atualização de telemetria a cada ~2 s. Um pulso pode ser encurtado se a demanda
  calculada cair enquanto ele está ativo.
- O intervalo mínimo agora é 10 s desligado, contado da última transição. Com pulso máximo de
  20 s isso limita a operação a 2/3 de ciclo no pior caso; para um aquecedor nominal de 10 W,
  a potência média teórica máxima fica em ~6,7 W. A placa apresentada pelo usuário informa
  12 V / 10 W (~0,83 A na potência nominal); tensão/corrente reais não foram medidas.
- A integral deixou de ser zerada ao cruzar 37 °C: acumula enquanto há erro positivo e é
  reduzida gradualmente quando a temperatura passa da meta, com limites para evitar acúmulo
  durante a saturação. A motivação foi a telemetria anterior: após chegar à meta, a demanda
  desaparecia e a temperatura depois caiu até 36,5 °C.
- Upload verificado: 32.238 bytes de Flash (18 bytes livres) e 983 bytes de RAM. BOOT_COUNT=141
  restaurou a trava de CO₂; automático desligado, `co2_valid=0`, válvula fechada em toda a
  observação.
- Em aproximadamente 5 min de telemetria, a leitura começou em 36,9 °C, chegou a 37,1 °C,
  depois oscilou para baixo até 36,5 °C. A demanda cresceu gradualmente e os pulsos chegaram
  a ~14 s ligado / 10 s desligado; a temperatura voltou a 37,0–37,1 °C por cerca de 1 min,
  sem ultrapassar 37,1 °C. Depois caiu novamente a 36,7 °C com novos pulsos de ~12 s. A faixa
  ainda não se manteve por toda a janela; são necessárias mais observações e não há espaço
  suficiente na Flash para adicionar recursos sem otimização prévia.
- Referências técnicas consultadas: [manual OMEGA CN Series](https://assets.omega.com/manuals/M4636.pdf)
  descreve integral para erro persistente e derivada como antecipação baseada na taxa; o
  [manual OMEGA CN2116](https://assets.omega.com/manuals/M2950.pdf) descreve ajuste de saída
  (cutback) para limitar ultrapassagem; a [nota Watlow sobre posição do sensor](https://www.watlow.com/resources-and-support/engineering-tools/knowledge-base/sensor-placement-in-a-thermal-system)
  explica que o atraso entre fonte térmica, sensor e carga altera a oscilação. Para esta
  montagem, continuam desconhecidos a posição térmica exata do DHT, a tensão no aquecedor e
  a perda de calor da câmara.

## Acompanhamento térmico após retenção da integral

- 2026-10-15, BOOT_COUNT=142. A leitura começou em 37,1 °C, tocou 37,2 °C nos primeiros
  segundos e depois caiu gradualmente até 36,5 °C. A demanda aumentou com a queda; a saída
  aplicou pulsos progressivos, chegando a cerca de 12–14 s ligada com 10 s mínimos desligada.
- A temperatura recuperou 37,0 °C após cerca de 3 min e oscilou entre 37,0–37,1 °C por
  aproximadamente 1 min. Depois caiu novamente até 36,7 °C e recuperou outra vez; perto do
  fim da janela, permaneceu entre 37,0–37,1 °C por cerca de 1 min, sem aquecimento ativo.
  O último dado foi 36,9 °C com um pulso de ~6,3 s em andamento. A amostra confirma que a
  integral retida volta a pedir calor após atravessar a meta, mas a incubadora ainda alterna
  períodos abaixo e dentro da faixa de 36,9–37,1 °C; a estabilidade prolongada não está
  comprovada.
- Durante todo o monitoramento, `co2_range_lock=1`, `co2_valid=0`, controle automático de
  CO₂ desligado e válvula fechada. Os números brutos do sensor não são concentração válida.

## Repetição térmica com condições contínuas

- 2026-10-15, BOOT_COUNT=143. Início em 36,8 °C; após uma queda inicial até 36,6 °C, os
  pulsos foram crescendo conforme a demanda. A leitura chegou a 36,9–37,0 °C em ~2 min.
- Na janela total de ~5 min, a temperatura variou entre 36,6 e 37,0 °C, sem exceder 37,0 °C.
  Perto da meta, o PID pediu pulsos de ~4–6 s; em 36,7–36,8 °C, a demanda aumentou para
  ~10–12 s. Houve uma queda até 36,7 °C seguida de recuperação gradual, e o último trecho
  ficou em 37,0 °C com aquecedor desligado. Melhor que a janela anterior (sem pico de 37,2 °C),
  mas ainda há desvios de até 0,4 °C abaixo da meta; seguir acompanhando antes de retunar.
- `co2_range_lock=1`, `co2_valid=0`, `co2_enabled=0`, `valve_open=0` durante toda a sessão.

## Terceira janela de acompanhamento térmico

- 2026-10-15, BOOT_COUNT=144, ~5 min. A amostra inicial foi 37,0 °C; caiu a 36,6 °C no
  primeiro minuto, enquanto o pedido de calor crescia de ~2 s para ~12 s. A temperatura
  voltou a 37,0 °C em cerca de 2,5 min, permaneceu perto da meta por ~40 s e então oscilou
  até 36,7 °C. No fim da janela recuperou 36,9 °C, com demanda de ~7,4 s e relé desligado.
- Faixa observada 36,6–37,0 °C, sem leitura acima da meta. O vale de 0,4 °C abaixo se repetiu;
  o PID adaptou a duração dos pulsos e recuperou a temperatura, porém ainda leva minutos para
  corrigir uma queda. Nenhuma alteração de ganho foi feita nesta sessão.
- CO₂ permaneceu travado e inválido (`co2_range_lock=1`, `co2_valid=0`); controle desligado e
  válvula fechada.

## Ajuste proporcional térmico de +20%

- 2026-10-15, BOOT_COUNT=147. O ganho proporcional subiu de 20.000 para
  24.000 ms/°C; integral, derivada, pausa mínima de 10 s, pulso máximo de 20 s e corte
  independente em 37,1 °C permaneceram iguais. O aquecedor flexível mostrado pelo usuário
  está identificado como 12 V / 10 W (corrente nominal calculada: ~0,83 A; corrente e tensão
  efetivas ainda não medidas).
- Em quase 3 min de observação, a temperatura começou em 36,6 °C, oscilou entre 36,5 e
  36,8 °C no primeiro minuto e chegou a 37,0 °C em aproximadamente 2 min. No trecho final
  ficou entre 36,9 e 37,0 °C, sem ultrapassar 37,0 °C. A demanda caiu gradualmente perto da
  meta; os pulsos finais ficaram em torno de 4–6 s, separados pelo intervalo mínimo.
- Esta janela mostrou recuperação contínua e uma faixa observada mais estreita no fim; ainda
  é curta para provar estabilidade prolongada ou atribuir a melhora somente ao Kp. Manter a
  observação antes de qualquer outro ajuste. CO₂ permaneceu travado e inválido
  (`co2_range_lock=1`, `co2_valid=0`), automático desligado e válvula fechada.

## Confirmação prolongada do Kp térmico

- 2026-10-15, BOOT_COUNT=148, cerca de 5 min com Kp=24.000 ms/°C. A temperatura iniciou em
  36,8 °C, caiu até 36,7 °C no primeiro minuto e alcançou 37,0 °C em ~2 min. Depois oscilou
  principalmente entre 36,7 e 37,0 °C, com ciclos de queda gradual e recuperação; terminou
  em 37,0 °C. Não houve leitura acima de 37,0 °C nem corte de segurança.
- Em 36,7 °C, o PID aumentou o pedido até ~11,8 s; perto de 36,9 °C, os pedidos ficaram em
  ~4–7 s. Em 37,0 °C a demanda foi zero e o relé permaneceu majoritariamente desligado. A
  tendência variou aproximadamente de −0,2 a +0,1 °C/min. O ganho maior sustenta recuperação,
  mas não eliminou oscilações de até 0,3 °C na leitura; manter o ajuste atual e observar antes
  de alterar mais parâmetros.
- CO₂ seguiu travado e inválido (`co2_range_lock=1`, `co2_valid=0`), com controle automático
  desligado e válvula fechada. Os valores brutos de CO₂ não são concentração válida.

## PI/D de manutenção no setpoint

- 2026-10-15, BOOT_COUNT=150: a observação anterior mostrou que o cálculo permitia
  demanda em 37,0 °C, mas a condição `safeToHeat` ainda exigia temperatura estritamente
  abaixo do setpoint. O relé, portanto, não aplicava a correção no alvo. Ajustada a condição
  para permitir aquecimento em 37,0 °C; acima do alvo, a saída continua inibida e o corte
  rígido em 37,1 °C permanece. Compilado e gravado com 32.240 bytes de Flash e 983 bytes de
  RAM.
- 2026-10-15, BOOT_COUNT=152, quase 5 min. A leitura iniciou em 36,9 °C, caiu a 36,6 °C e
  recuperou até 37,0 °C em cerca de 3 min. No trecho final oscilou entre 36,9–37,1 °C por
  aproximadamente 2 min; o corte desligou o aquecedor quando a leitura atingiu 37,1 °C.
  Perto da meta, apareceram pedidos de ~1,6–3,0 s em 37,0 °C e pulsos curtos; entre 36,6 e
  36,7 °C, os pedidos cresceram para ~12–13 s. Não houve leitura acima de 37,1 °C.
- A mudança permite correção no próprio setpoint e a faixa do trecho final ficou dentro de
  ±0,1 °C, mas a precisão do DHT22 e a duração curta impedem concluir controle físico exato
  ou estabilidade de longo prazo. Repetir em outra janela antes de retunar. CO₂ permaneceu
  travado/inválido (`co2_range_lock=1`, `co2_valid=0`), controle desligado e válvula fechada.

## Janela prolongada após habilitar trim no setpoint

- 2026-10-15, BOOT_COUNT=152, telemetria contínua por aproximadamente 6 min. A temperatura
  iniciou em 36,9 °C, caiu a 36,6 °C e voltou à meta em ~3 min. Depois oscilou entre
  36,6–37,1 °C; no trecho final ficou principalmente em 36,9–37,0 °C. O relé desligou ao
  atingir 37,1 °C e não houve leitura acima desse limite. Em 37,0 °C, a demanda de manutenção
  ficou em ~1,6–4,2 s; abaixo da meta cresceu para ~5–13 s conforme a queda e a tendência.
- A nova condição permitiu pulsos no setpoint, mas a leitura ainda variou até 0,5 °C desde o
  vale frio. A última janela, por sua maior duração, mostra recuperação e manutenção perto de
  37 °C, mas ainda não prova uniformidade da câmara nem a precisão real do DHT22.
- CO₂ permaneceu `co2_range_lock=1`, `co2_valid=0`, `co2_enabled=0`, `valve_open=0`; a leitura
  bruta do sensor continua inválida e não foi usada na análise.

## Repetição térmica com inicialização quente

- 2026-10-15, BOOT_COUNT=153, aproximadamente 4 min 48 s. A leitura inicial foi 37,1 °C;
  após o reinício, caiu gradualmente até 36,7 °C durante o primeiro minuto. O PID ampliou
  os pulsos conforme a queda; a leitura retornou a 37,0 °C após cerca de 2,5 min.
- No restante da janela, a leitura ficou entre 36,9–37,1 °C, sem passar do corte. Em 37,0 °C,
  a demanda de manutenção ficou aproximadamente em 1,4–2,7 s e foram observados pulsos curtos;
  em 36,7–36,9 °C, pedidos ficaram entre ~2,4–10 s. A tendência no trecho final aproximou-se
  de zero e a temperatura permaneceu em 36,9 °C.
- O padrão confirma recuperação e manutenção dentro de ±0,1 °C no trecho estabilizado, mas o
  vale pós-reinício chegou a 0,4 °C abaixo do alvo. O boot reinicializa a integral e os sensores
  ainda têm precisão limitada; não interpretar o reinício como uma perturbação normal de uso.
  CO₂ permaneceu travado/inválido (`co2_range_lock=1`, `co2_valid=0`), automático desligado e
  válvula fechada.

## Nova repetição da faixa térmica estabilizada

- 2026-10-15, BOOT_COUNT=153, 4 min 48 s de telemetria. A temperatura começou em 37,1 °C,
  passou a 37,0 °C e caiu até 36,7 °C durante o primeiro minuto. A ação do PID aumentou em
  resposta; a leitura retornou a 37,0 °C perto de 2,5 min. Depois permaneceu majoritariamente
  em 36,9–37,0 °C, tocando 37,1 °C em leituras breves. O aquecedor foi desligado ao atingir
  37,1 °C e nenhum valor maior foi observado.
- A repetição confirma a faixa final de ±0,1 °C por aproximadamente 2 min após recuperação,
  enquanto o vale transitório pós-reset foi 0,3–0,4 °C abaixo da meta. A abertura do monitor
  serial reinicia o Uno e zera os estados voláteis do PID; essa queda inicial não equivale a
  uma operação contínua sem reset. CO₂ permaneceu travado/inválido, automático e válvula OFF.

## Diagnóstico do CO₂ com a porta aberta

- 2026-10-15, BOOT_COUNT=156–158. O usuário confirmou a porta aberta e desligou o aquecimento
  pelo botão. Telemetria confirmou aquecimento OFF, controle automático de CO₂ OFF e válvula
  fechada. Temperatura principal caiu de ~36,7 °C para 35,6 °C antes do upload e continuou
  caindo após o reinício; temperatura interna ficou em 30,6 °C, abaixo do limiar de 31 °C do
  ventilador, que permaneceu OFF.
- A leitura serial bruta caiu de ~20.443 para ~20.218 ppm em ~67 s. Depois do upload, caiu de
  ~19.994 para ~19.840 ppm em ~63 s. Como `co2_range_lock=1` e `co2_valid=0`, esses valores
  e sua variação não medem concentração nem taxa real de vazamento. Naquele momento, a falta
  de aproximação a 400 ppm pareceu inesperada; após o usuário informar que o rótulo indica
  `1–10% VOL`, essa comparação deixou de ser válida sem confirmar se a variante mede abaixo
  de 1%. O ensaio não isola defeito do sensor, escala, condicionamento, alimentação ou
  comunicação.
- A trava é uma proteção persistida pelo firmware: é acionada por leitura bruta a partir de
  60.000 ppm ou salto de pelo menos 15.000 ppm entre amostras; bloqueia o controle automático,
  não a leitura do sensor. A origem exata da trava atual antecede este trecho de log. A tela
  agora exibe o número reportado pelo protocolo com o cabeçalho `BRUTO ppm` durante essa
  proteção. A taxa ppm/min continua indisponível enquanto os dados não forem considerados
  válidos.
- Firmware compilado e gravado; após o upload, BOOT_COUNT=158 e os estados persistidos
  confirmaram aquecimento e controle de CO₂ desligados, válvula fechada. Compilação: 32.166
  bytes de Flash e 983 bytes de RAM. O ajuste Kp=32.000 ms/°C foi testado antes da abertura,
  mas este ensaio foi interrompido ao abrir a porta e desligar o aquecimento; não usar os
  dados seguintes para avaliar estabilidade térmica em operação fechada.
- A pedido do usuário, a faixa vertical de estado da tela agora fica vermelha sempre que a
  trava persistida está ativa, inclusive quando a temperatura estiver dentro da faixa normal.
  O valor continua identificado como `BRUTO ppm`. Compilado e gravado em BOOT_COUNT=160;
  `STATUS` confirmou `co2_range_lock=1`, aquecimento e CO₂ OFF, válvula fechada e ventilador
  OFF (sensor interno em 30,6 °C). Nova compilação: 32.182 bytes de Flash e 983 bytes de RAM.

- Após novo ciclo de energia mais longo, BOOT_COUNT=164. A trava persistiu (`co2_range_lock=1`);
  `STATUS` confirmou leitura inválida, CO₂ e aquecimento desabilitados, válvula fechada e
  ventilador desligado. O sensor continuou respondendo: ~18.297 ppm em 13,5 s, caindo para
  ~18.106 ppm em ~104 s. Um único registro de 500 ppm apareceu antes do BOOT_COUNT=162 causado
  pela abertura do monitor; as amostras contínuas após esse reset voltaram perto de 19.063 ppm,
  portanto o registro isolado não comprova estabilidade em 500 ppm. Um clique curto no botão
  físico não alterou a trava nem a sequência de leituras.
- A origem conhecida da trava persistente desta sessão é o comando deliberado `CO2 LOCK`,
  registrado em BOOT_COUNT=122; os boots seguintes apenas restauraram o marcador EEPROM. Isso
  é uma trava de controle do firmware, não indicação de que o próprio sensor parou ou entrou
  em modo de calibração. O manual define calibração zero no pino HD ao manter nível baixo por
  mais de 7 s; o clique curto relatado não satisfaz essa condição.
- O usuário informou que a etiqueta indica `1–10% VOL`; as fotos locais mostram o gabinete,
  a câmara e o cilindro, mas não permitem ler a etiqueta. Não usar 400 ppm como referência até
  confirmar a faixa mínima dessa variante. A leitura bruta de ~18k está acima de 1%, porém
  continua inválida pelo bloqueio e não pode orientar dosagem.
- O CSV elétrico local nomeia a peça como `Sensor CO2 10k` e liga VCC a 5V, GND a GND,
  RX ao Arduino D5 e TX ao D12, compatível com `SoftwareSerial(12,5)` no firmware. Isso confirma
  a intenção do mapeamento, mas o nome `10k` diverge da etiqueta `1–10% VOL`; não prova a
  variante nem a escala UART. As leituras brutas desta sessão (~14.000 ppm) também não resolvem
  a divergência porque continuam bloqueadas e não foram comparadas com uma referência.
- O manual oficial v2.6 lista faixa selecionável até 50.000 ppm, extensão máxima de 150.000 ppm,
  T90 <30 s e fonte de 5,0±0,1 V com pelo menos 150 mA. Ele não documenta a codificação UART
  acima de 65.535 ppm; o manual v2.4 citado acima documenta dois bytes em ppm e opções de faixa
  inconsistentes entre tabelas. O limite uint16 de ~6,55% é compatível com o relato do problema
  perto de 6%, mas ainda não prova a causa nem confirma como esta unidade de 1–10% codifica a
  resposta. A meta de 50.000 ppm permanece dentro do limite atual do decoder.
- Próximas verificações: confirmar a identificação/faixa da unidade por foto legível e medir
  5,0±0,1 V no próprio conector com o sensor operando. Manter a trava até esclarecer a UART e
  estabelecer uma referência válida; não enviar calibração de zero ou `CO2 ACK` por causa de
  um registro isolado.
- Depois de ~3 min desde o BOOT_COUNT=164, a leitura bruta caiu de ~17.800 para ~14.784 ppm
  ao longo de cerca de 2 min. O sensor segue respondendo, mas a leitura permanece inválida e a
  trava ativa. Uma revisão antiga do manual informa pré-aquecimento de 3 min, mas a versão 2.6
  (2022-04) e a página oficial atual informam 10 s. Como a etiqueta e o número de série não
  identificam qual revisão/firmware rege esta unidade, não atribuir a queda ao pré-aquecimento;
  ela não demonstra calibração, retorno a uma concentração conhecida ou que o clique físico
  causou a mudança.
- Na continuação da mesma sessão, a leitura bruta caiu de 14.652 para 14.613 ppm em 16,9 s
  (aprox. −138 ppm/min). A temperatura principal ficou em ~23,9–24,0 °C e a interna em
  ~29,4 °C; CO₂, válvula, aquecimento e ventilador permaneceram desligados. Essa é somente a
  inclinação do valor UART inválido, não uma taxa confirmada de perda de CO₂.
- Nova janela da mesma sessão: 14.444 para 14.244 ppm em 84,3 s (aprox. −142 ppm/min), com
  trava persistente e atuadores desligados. A temperatura principal variou ~23,6–23,8 °C,
  umidade ~55,5–56,1% e sensor interno ~29,4–29,5 °C. A inclinação é consistente com as
  anteriores, mas permanece apenas uma deriva da leitura inválida, sem referência externa.
- Continuação: de 14.062 para 13.938 ppm em ~56 s (aprox. −133 ppm/min). A trava continuou
  ativa (`co2_valid=0`, `co2_range_lock=1`) e CO₂, válvula, aquecimento e ventilador permaneceram
  OFF. Temperatura principal ~23,5–23,6 °C, RH ~56,0–56,2% e sonda interna ~29,5 °C. A deriva
  permanece consistente, mas não é uma taxa de vazamento validada.
- Janela seguinte: 13.934 para 13.838 ppm em ~46 s (aprox. −125 ppm/min). Temperatura ~23,5 °C,
  RH ~56,3–56,5%, sonda interna ~29,5 °C; trava ativa e todos os atuadores OFF. Segue como
  deriva do número UART sem validação de concentração.
- Resumo de uma janela longa do mesmo BOOT_COUNT=164: de 14.444 ppm em 424,6 s para 13.730 ppm
  em 754,2 s, média de aproximadamente −130 ppm/min ao longo de 5,5 min. A deriva não estava
  estabilizando em 10.000 ppm nesse intervalo; como a trava permaneceu ativa, isso não informa
  a concentração real nem confirma que exista um limite inferior de 10.000 ppm.
- Continuação da janela longa: de 14.444 ppm em 424,6 s até 13.559 ppm em 833,9 s, média de
  −130 ppm/min por ~6,8 min. A leitura não mostra platô nessa janela; permanece inválida pela
  trava firmware e não pode ser interpretada como concentração ou vazamento real.
- Continuação: de 13.726 ppm em 756,3 s para 13.373 ppm em 913,7 s, média de −135 ppm/min em
  ~2,6 min. `co2_valid=0`, `co2_range_lock=1` e todos os atuadores OFF permaneceram constantes;
  a deriva UART segue monotônica sem representar uma taxa real de perda.
- Continuação até 1.010,4 s: 13.726 ppm em 756,3 s para 13.170 ppm, média de ~−131 ppm/min em
  ~4,2 min. A placa permaneceu no BOOT_COUNT=164, com trava persistente, leitura inválida e
  atuadores OFF. A série continua sem indicar platô; requer comparação com tensão/alimentação
  medida e referência externa antes de tirar conclusão sobre concentração.
- Continuação até 1.058,8 s: leitura bruta em 13.068 ppm; de 13.726 ppm em 756,3 s representa
  média de ~−129 ppm/min em ~5 min. `co2_valid=0`, trava ativa, temperatura ~23,1 °C, RH ~57,2%
  e atuadores OFF. Ainda é deriva do valor UART sem validação externa.
- Continuação até 1.153,4 s: 12.872 ppm, mantendo a média em ~−129 ppm/min desde 756,3 s.
  Temperatura principal ~23,0–23,1 °C, sonda interna ~29,6–29,7 °C e RH ~57,3–58,0%; trava
  ativa e atuadores OFF. A inclinação quase constante durante essa janela longa não distingue
  deriva do sensor de mudança real no gás sem uma referência independente.
- Continuação até 1.204,3 s: leitura UART bruta em 12.762 ppm; de 13.726 ppm em 756,3 s, média
  ~−129 ppm/min ao longo de ~7,5 min. O contador de `millis()` avançou continuamente, sem boot
  ou falha de leitura aparente; `co2_valid=0`, trava ativa e todos os atuadores OFF. Isso confirma
  comunicação contínua, não a exatidão do valor recebido.
- Continuação até 1.515,8 s: leitura bruta 12.111 ppm; de 13.726 ppm em 756,3 s, média de
  ~−128 ppm/min em ~12,7 min. A temperatura ficou ~22,8–23,0 °C e a sonda interna ~29,6–29,7 °C;
  trava ativa, sem reinício aparente e todos os atuadores OFF. A deriva continua sem platô
  observado, mas continua inválida para controle e diagnóstico quantitativo de vazamento.
- Continuação até 1.604,3 s: 11.923 ppm, sem platô observado. De 13.726 ppm em 756,3 s, média
  ~−128 ppm/min em ~14,1 min. Temperatura ~22,7–22,8 °C, RH ~58,4–58,9%, sonda interna
  ~29,6–29,7 °C; trava ativa e atuadores OFF. A proximidade futura de 10.000 ppm, se ocorrer,
  não deve ser tomada como limite da variante sem confirmação documental ou referência.
- Continuação até 1.748,1 s: 11.656 ppm. De 13.726 ppm em 756,3 s, média de ~−125 ppm/min ao
  longo de ~16,5 min; a janela recente de ~65 s caiu 127 ppm (~−117 ppm/min), confirmando que a
  oscilação curta anterior não era um platô. Trava ativa, leitura inválida e atuadores OFF.
- Continuação até 1.901,4 s: 11.365 ppm. De 13.726 ppm em 756,3 s, média de ~−124 ppm/min em
  ~19,1 min; a janela mais recente de ~68 s caiu 121 ppm (~−107 ppm/min). Ainda não há platô
  confirmado; a trava e todos os atuadores seguem OFF/ativos conforme esperado.
- `STATUS` em 2.023,6 s confirmou BOOT_COUNT=164, `co2_valid=0`, `co2_range_lock=1` e CO₂,
  válvula, aquecimento e ventilador OFF. Leitura bruta em 11.116 ppm. De 13.726 ppm aos 756,3 s
  para 11.116 ppm aos 2.023,6 s, média ~−124 ppm/min em ~21,1 min. Sem reboot, a deriva do
  número UART continua; não representa concentração validada.
- Comparação com a seção anterior “Resposta do CO₂ e aquecimento após reinstalar o sensor”:
  naquela inicialização, sem injeção, o número reportado subiu de ~706 ppm para ~10.000 ppm;
  neste BOOT_COUNT=164, sem injeção e com a válvula sempre fechada, caiu de ~18.297 ppm para
  ~12.659 ppm após ~21 min. A deriva de milhares de ppm em sentidos opostos, repetida sem
  acionamento da válvula, favorece instabilidade/acomodação ou escala do sensor como hipótese
  para esses valores; não quantifica vazamento. Manter `co2_valid=0`, sem exibir taxa válida ou
  permitir controle automático até referência independente e identificação da unidade.
- Revisão do parser local `NDIRZ16::measure()`: cada amostra numérica registrada exige sync
  `0xFF`, comando de resposta `0x86` e checksum de quadro aceito; falha de leitura produziria
  `co2_ppm=-1` e `EVENT,co2_sensor_read_failed`. Não houve esse evento nem amostras `-1` na
  janela observada, então a UART entrega quadros estruturalmente válidos. `co2_valid=0` nessa
  sessão significa a trava persistida do firmware, não falha do parser. Isso reduz a hipótese
  de simples desalinhamento UART, mas não valida a escala, calibração ou concentração física.
- Comparação histórica do firmware: antes de `bdde11f` (`Handle MH-Z16 readings as ppm values`),
  `getppm()` era atribuído a `bool`. Como a biblioteca retorna `-1` em falha, a conversão em C++
  tratava essa falha como `true` e o código podia reutilizar `mySensorCO2.ppm` anterior como se
  fosse uma nova leitura. `bdde11f` corrigiu a condição para guardar o retorno em `int32_t` e
  aceitar apenas valores `>=0`. Esse defeito histórico poderia gerar amostras antigas congeladas
  em versões anteriores; está corrigido no firmware atual e não explica a deriva contínua atual,
  cujos quadros passam no parser.
- Referências: [manual MH-Z16 v2.6](https://www.winsen-sensor.com/d/files/manual/mh-z16.pdf),
  [página oficial do MH-Z16](https://www.winsen-sensor.com/product/mh-z16.html),
  [manual MH-Z16 v2.4](https://www.winsen-sensor.com/d/files/MH-Z16.pdf).
- Teste de resposta ao retirar o sensor da caixa: durante a transição, o valor UART caiu de
  ~11.017 para 8.261 ppm e seguiu descendo até 965 em cerca de 2 min. O último trecho foi
  2.599 → 965 ppm em ~46 s; a temperatura ambiente ficou em 22,5–22,6 °C e a umidade em
  ~58,6–58,9%. BOOT_COUNT permaneceu 164, trava persistente (`co2_valid=0`,
  `co2_range_lock=1`) e todos os atuadores ficaram desligados. A resposta forte e contínua à
  mudança de ambiente mostra que a saída UART não estava simplesmente congelada; é compatível
  com a leitura anterior refletindo CO₂ elevado dentro da caixa e a leitura diminuindo fora
  dela. Como a escala/calibração ainda não foi validada, esses números e sua taxa de transição
  não devem ser interpretados como concentração ou taxa real de vazamento.
- Revisão adicional da documentação oficial: o manual v2.4 descreve a resposta UART `0x86` como
  concentração em dois bytes (`HIGH*256+LOW`) e o comando `0x99` para configurar a faixa. O
  firmware local só consulta `0x86`, lê os dois bytes como ppm e não configura a faixa. Já o
  manual v2.6 lista faixas selecionáveis até 0–10%/0–15% VOL e extensão até 150.000 ppm, mas não
  esclarece como essas faixas maiores são codificadas no UART. Assim, o teto de 65.535 do formato
  antigo (6,5535% se a unidade continuar ppm) é uma hipótese plausível para o loop observado perto
  de 6%, mas ainda não está provado que a placa use esse protocolo/faixa. Não mudar parser nem
  enviar `0x99` sem identificar a revisão exata e obter a codificação da Winsen; capturar o quadro
  UART bruto em bancada será o próximo teste de firmware apropriado.
