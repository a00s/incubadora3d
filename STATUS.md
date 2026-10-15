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
