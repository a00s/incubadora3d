# Memória local do projeto

## Trabalho ativo — controle térmico e visor, 2026-10-27

Atualização00:24 de28/10, após retomada do objetivo: supervisor74644 e
coletor70766 vivos; sem EVENT,door desde HEAT ON23:40. Referência37,0 °C
na imagem atual00:23:38, Arduino37,11 °C. Últimos20min Arduino36,74–37,18 °C,
média36,9576 °C;23amostras acima37,1. Não atingiu corte experimental37,2.
O máximo37,18 ocorreu00:13:27; substitui máximos parciais anteriores.
Dados `docs/ensaios/patamar_pote_lado_0024_2026-10-28.json`.
Observador de fotos anterior terminou (PID70767 ausente); coleta retomada
00:23:52 com mesmo script/pasta, índice061 em diante, sessão81596. Serviço
RoomCam segue streaming, quadro0,11s; sem segundo RTSP/inferência.
Teste físico de porta permanece pendente. Supervisor expira~01:02.


Estado00:05 de28/10: teste de abertura solicitado, ainda sem resposta nem
EVENT,door novo. Próximo passo físico indispensável: abertura30s com modo
porta, sem mover água/sondas, e retomada pelo botão. Não inventar execução.
Patamar parcial desde primeira chegada37:12,86min, Arduino36,74–37,11 °C,
média36,921 °C, uma amostra acima37,1; registro em
`docs/ensaios/patamar_pote_lado_parcial_2026-10-28.json`.
Supervisor74644 confirmado vivo00:05; timeout às~01:02 desliga HEAT,
assim como leitura>=37,2 °C/falha de dados. CO₂ permanece habilitado.
Essa interrupção programada não é emergência de firmware39 °C.


Atualização00:02 em28/10: montagem com pote AO LADO, sem contato direto
com aquecedor. Recuperação desde23:40 chegou a37,05 °C às23:52 e máximo
37,11 °C às23:59. Referência37,0 °C às23:55;36,8 °C às00:00;36,9 °C
às00:02. Ensaio parcial arquivado em `pote_lado_antes_porta_2026-10-28.*`.
Supervisor anterior terminou por TRANSFERÊNCIA, apesar do rótulo legado
`released_after_validation`: não significa aprovação completa. Novo supervisor
vivo `supervisionar-porta-pote-lado.py`, PID74644, saída
`supervisao-porta-pote-lado.json`, sessão36062, limite37,2 °C/timeout1h.
Permite pausa pelo botão sem comandar HEAT ON na entrada. Mesmo log e
BOOT33, coletor70766. Não reiniciar serial/firmware durante o teste.
Solicitado ao usuário teste normal de porta30s, sem mover água/sondas;
aguardar confirmação/eventos novos. Câmera observador70767 termina cerca
de00:09; conferir processo antes de continuar coleta de fotos.


Atualização após manutenção do ventilador (~23:40): usuário confirmou serviço
feito e porta fechada. ALL OFF foi enviado para manutenção; portanto essa
retomada parte da integral inicial, não é teste isolado de pausa de porta.
Relato físico NOVO: pote agora AO LADO do aquecedor, sem ficar sobre ele;
usuário descreve aquecimento indireto pelo piso de alumínio. Substitui a
montagem anterior de canto encostado. Não presumir volume restante nem RH.
Sem novo ajuste de firmware/offset nesta mudança. CO₂ habilitado confirmado
na telemetria; retomada térmica supervisionada por
`/tmp/incubadora-telemetria/supervisionar-pos-ventilador.py`, saída
`supervisao-pos-ventilador.json`, usando o mesmo log calib-agua25/BOOT33.
Conferir estado vivo antes de afirmar que continua aquecendo.
Etapa anterior foi interrompida pela manutenção, não por limite térmico:
máximo Arduino37,11 °C; referência atingiu37,0–37,1 °C nas capturas.
Esses dados não validam a montagem nova nem uso com células.


**Estado ~23:11: ensaio vazio, sem células (relato do usuário). NÃO aprovado
para uso com células; controle térmico ainda tem picos e diferença entre sondas.**

Resultados verificados: a revisão de tendência filtrada, gravada ~17:29,
falhou no ensaio supervisionado às 17:42 (37,20 °C, HEAT OFF confirmado).
O controle foi reabilitado posteriormente, sem novo ACK serial; origem não
estabelecida. Entre as leituras das horas seguintes, Arduino atingiu 37,45 °C.
Às 22:01:32, câmera atual mostrou referência37,9 °C e Arduino~37,0 °C.
Não atribuir todos os picos à calibração. Arquivo completo, parâmetros e
patch reprodutível do firmware realmente ensaiado em
`docs/ensaios/filtro_tendencia_2026-10-27.{csv,json,patch}`.
Etapas anteriores, incluindo recuperação com pico37,39 °C, também arquivadas.

Relato físico do usuário ~22:11: recipiente estava SECO; porta foi aberta,
fechada e adicionados25mL em OUTRO pote, com apenas um canto tocando o
 aquecedor. Usuário pediu manter exatamente assim por enquanto e comparar
sem contato depois que estabilizar em37 °C. Não alterar essa montagem sem
nova orientação. Evaporação/umidade dessa montagem ainda não medidas.
Hipótese: secagem e contato térmico mudam a carga térmica e a evaporação;
isso não é explicação verificada de todos os erros do controle.
Arduino NÃO mede atualmente umidade da câmara (`rh_pct=nan`); DHT22 mede
somente temperatura da eletrônica. Os95% citados pelo usuário são relato
anterior, não leitura presente da telemetria.

Firmware atual gravado e verificado ~23:09: TODOS os cinco campos numéricos
(CO₂, temperatura da câmara, temperatura interna, ppm/min, cm³/h) usam cache
por caractere. Só apaga a célula cuja forma mudou; mudança apenas de cor
repinta sem apagar. Fonte grande tem avanço13px, pequena7px, confirmado
pela decodificação das fontes reais no teste. Campos encurtados apagam sufixos.
Visor verifica atualizações ~640ms durante atendimento de entradas, fora da
espera2s do ciclo de CO₂; sensor DS18B20 converte em >=800ms. O CO₂ continua
lido no ciclo principal. Testes de todos os cinco campos, mesma leitura sem
SPI, cores sem apagar, mudança de comprimento, cadência e modo porta passaram;
também passaram os quatro testes térmico/porta/CO₂. Flash32160bytes, RAM
estática1121bytes. As alterações gráficas não mudaram ganhos/cortes. Depois delas houve somente
o ajuste operacional de offset abaixo.

Hardware confirmado pelo usuário em imagens de anúncios: tela AZDelivery
1,77pol ST7735(S),128×160,SPI, com conversor TXS0108E. Driver configurado
Ucglib_ST7735_18x128x160_HWSPI corresponde à família. Fichas oficiais:
https://www.az-delivery.de/en/products/1-77-zoll-spi-tft-display e
https://www.ti.com/product/TXS0108E . CSV documenta VA3,3V/VB5V, A→tela,
B→Uno, OE via resistor aVA. Qualidade elétrica não medida. Fontes AZ têm
especificação2,7–3,3V e diagrama de ligação do módulo com VCC5V; identificar
versão/regulador da placa antes de recomendar mudança de alimentação.
O intervalo de ~2,35s no desenho antigo foi medido no log e explicado pela
espera do programa; não atribuir automaticamente a driver/conversor.

Ajuste operacional gravado23:09: offset de+1,575 para+1,175 °C (−0,4 °C).
Base: últimos10min antes da interrupção tiveram média36,965 °C no Arduino,
faixa36,83–37,14 °C; referência repetiu36,5–36,6 °C nas imagens23:00/23:06
e anteriores. Fonte/dados em campos_parciais_antes_offset_2026-10-27.*.
É alinhamento operacional do ponto de referência desta montagem: referência
apoiada em metal, Arduino livre no ar; NÃO calibração comum de ambos sensores.
Ainda precisa validação independente no novo patamar e pico. Ganhos, período,
corte normal37,1 °C e emergência travada39 °C mantidos. Todos os testes passaram.

Coleta viva: `/tmp/incubadora-telemetria/coleta-calib-agua25-20261027.log`;
fotos/metadados em `calib-agua25-camera/`; BOOT33 (descartar trechos pré-boot).
Supervisor `supervisao-calib-agua25.json`, script `supervisionar-calib-agua25.py`.
Retomada automática do ensaio confirmada23:10:10 após20s de dados contínuos.
Às23:11, Arduino36,24 °C, ambos controles habilitados, aquecedor pulsando;
queda inicial inclui mudança do offset e interrupção para gravação.
Supervisor interrompe aquecimento a37,2 °C, falta de dados ou timeout1h
(após retomada, aproximadamente00:10). Verificar PID vivo e dados atuais.
CO₂ ativo. Manter25mL, só o canto do pote tocando e mesmas posições de sondas,
conforme pedido do usuário. Não declarar calibração/controle aprovados antes
 de comparar novo patamar e pico completo da referência e do Arduino.
Dados/limites e hashes em docs/ensaios/calibracao_operacional_agua25_2026-10-27.json.

Gravação da cadência foi autorizada pelo usuário ~22:30; ensaio anterior
interrompido com35,33 °C, não por falha térmica. Etapa seguinte interrompida
~22:41 para atender pedido de estender redesenho parcial a todos os campos,
com máximo36,76 °C. Não confundir interrupções gráficas com ensaios aprovados
ou com falhas por temperatura. Arquivos `agua25_pre_cadencia_2026-10-27.*`
e `visor_rapido_2026-10-27.*` preservam dados e fonte realmente gravada.

Câmera foi reposicionada; imagem atual está legível. Usar quadro inteiro
após mudanças; recorte antigo x640–905 não enquadra mais todos os dígitos.
Referência25,3 °C observada22:12:25 durante manipulação/reset. Usuário
anunciou reset de mínimo/máximo; confirmação visual dos novos extremos
pendente. Não adivinhar dígitos pequenos. Serviço existente127.0.0.1:8766;
não iniciar segundo RTSP, não mover PTZ nem expor configuração/credenciais.
CAD/STL/STEP/3MF sem mudanças; visualizador deve seguir servido em8081.

Este arquivo orienta sessões futuras. Conferir o código atual antes de assumir que
parâmetros aqui registrados continuam iguais. Não presumir que o firmware local
é idêntico ao gravado na placa sem verificar a gravação.

## Onde procurar

- `AGENTS.md`: regras de trabalho, entrega e restrições físicas.
- `README.md`, seção “Controle do Arduino pela USB”: sensores, ligações,
  calibração, comandos, telemetria e procedimento de compilação/gravação.
- `temperatura.ino`: fonte principal do Arduino, controle térmico/CO₂,
  leitura dos sensores, display, botões e modo porta.
- `firmware/incubadora/incubadora.ino`: link para `../../temperatura.ino`,
  não é um segundo firmware. `display_font.h` fica nessa pasta.
- `scripts/arduino.sh`: setup, compile, upload e monitor; padrão Uno R3,
  `/dev/ttyACM0`. Gravar reinicia/interfere no controle físico: não fazer
  automaticamente durante uma investigação apenas documental.
- `scripts/capture_serial.py`: captura da telemetria serial a 9600 baud.
- `scripts/test_heater_control.py`, `test_door_recovery.py`,
  `test_display_door.py`, `test_co2_control.py`, `test_co2_loss.py`:
  verificações do firmware; não substituem ensaio térmico físico.
- `arduino-libraries/NDIRZ16`: biblioteca local do sensor de CO₂.
- `cad/model.py` e demais scripts em `cad/`: fontes e ajustes do projeto 3D.
- `STATUS.md`: histórico técnico, estado geométrico e pendências físicas.
- `output/v59/`: STL/STEP, cópia versionada do 3MF e relatórios atuais.
- `output/incubadora_CrealityPrint_7.2.1.3mf`: projeto completo salvo pelo usuário;
  preservar configurações. `output/visualizador.html`: visualizador gerado;
  cópia servida em `/tmp/incubadora3d-viewer/index.html`, porta 8081.
- `Incubadora CO2 - CO2.csv`: tabela de ligações/pinagem dos componentes
  (começa pelas conexões da tela); consultar junto ao firmware para o esquema.

## Controle térmico conferido em 2026-10-27

- Câmara: DS18B20 em D4; eletrônica: DHT22 em D2; aquecedor em D6,
  saída ativa em LOW. Ligações detalhadas no README e no firmware.
- Meta 37,0 °C; offset aplicado na aquisição `+1.175 °C` (ajustado e gravado em 2026-10-27;
  validação térmica em andamento).
  O README registra o contexto e a posição diferente da referência.
- Pulsos atuais: até 17 s em toda a faixa, sem teto diferente perto da meta;
  pelo menos 20 s entre inícios e 3 s desligado. Tendência em janelas de 30 s;
  integral limitada a 17 s. Kp atual 9.000 ms/°C, Ki 1.000 ms/(°C·min),
  Kd 18.000 ms/(°C/min): aproximadamente 120 s de antecipação.
- `controlHeater` contém o PID e os cortes; `toggleDoorMode` pausa e
  restaura os controles. Conferir os nomes no código se forem refatorados.
- Pausa de porta preserva integral aprendida na RAM e invalida tendência;
  desligamento manual/falhas restauram a estimativa inicial de
  10.000 ms/20 s (50%) de manutenção, com base no histórico observado.
  A integral cresce só com tendência pronta, |taxa| <0,15 °C/min e saída não saturada;
  erro negativo a descarrega. PI/D atua nos dois lados da meta até corte 37,1 °C.
  Não há gravação desse aprendizado na EEPROM.
- README descreve os parâmetros do controle;
  para parâmetros executados, conferir as constantes e a lógica do firmware.

## Relato físico de 2026-10-27 — investigação pendente

- Usuário relata estabilidade na noite anterior; depois Arduino em 37 °C
  e referência inicialmente em 37,4 °C, chegando a 37,6 e 37,8 °C.
- Esclareceu que a subida ocorreu após abrir a porta e retomar o controle;
  a temperatura também baixa. Não tratar como mero offset constante.
- Vasilha sobre o aquecedor na parte inferior: 10 mL colocados à noite
  estavam esgotados pela manhã; depois acrescentou 50 mL. Não há horários
  e pesagens suficientes para calcular evaporação diária.
- Água e abertura alteram a carga térmica. Inércia e comportamento do PID
  são hipóteses a verificar com telemetria, não conclusões comprovadas.
- Ainda faltam leituras simultâneas dos dois sensores, estado do relé e
  curva temporal durante a recuperação. Nenhuma calibração ou lógica foi
  alterada nesta atualização da memória.

## Restrições físicas essenciais

- Borda fina da entrada da porta quebrou; não depender dela para peças novas.
- Porta se imprime com a frente externa plana na mesa (+Y do CAD para cima).
- Alterações de peças exigem STL/STEP, ambos os projetos completos 3MF,
  visualizador e verificações descritas no AGENTS.md.

## Câmera e coleta — 2026-10-27

- Acesso autorizado à câmera apontada ao termômetro: projeto
  `/home/x/projetos/acessocamera`; ler seu `AGENTS.md` antes de usar.
- Serviço existente: `http://127.0.0.1:8766`; cliente
  `/home/x/projetos/acessocamera/.venv/bin/roomcamctl`.
  Consultar status/frescor e capturar sem mover a câmera. Não ler nem expor
  `camera.local.json` ou linhas de comando RTSP que contenham credenciais.
- Visor principal: referência atual; mínimo à esquerda e máximo à direita,
  conforme usuário. Só transcrever números realmente legíveis.
- Usuário trocou o pote por placa de Petri mais baixa e de maior superfície;
  volume não informado. Relatou pouca perda no µ-Slide durante a noite,
  apesar de o reservatório secar; contribuição das tampas e da umidade é hipótese.
- Posição esclarecida pelo usuário: sensores separados por aproximadamente
  3 cm; referência apoiada na gaveta metálica, sonda Arduino pendurada livre
  no teto. A referência sofre influência térmica do metal e a sonda mede o ar;
  proximidade não garante igualdade durante transientes. O ajuste atual busca
  a temperatura da referência na região das amostras, não uma calibração
  metrológica intrínseca da sonda. Não mover sensores durante a comparação.
- Coleta anterior: `/tmp/incubadora-telemetria/coleta-20261027.log`.
  Após gravação: `coleta-pos-ajuste-20261027.log` na mesma pasta.
  Anotações e imagens temporárias nessa pasta; não presumir que sobreviverão
  a reinicializações. Conferir processo e data do log antes de afirmar coleta ativa.
- Abertura/fechamento para trocar água foram confirmados por toque longo;
  referência 33,4 °C versus Arduino 34,08 °C às 09:49, durante recuperação.
- Às 12:24–12:28, referência visual 36,2–36,3 °C; Arduino na última hora
  média 36,9707 °C, mínimo 36,76 e máximo 37,14 °C.
- Correção inicial de offset −0,75 °C (+2,325 → +1,575), compilada,
  testes do firmware aprovados e upload verificado por saída 0 às ~12:30.
  Ainda requer observar equilíbrio e recuperação; não declarar problema resolvido.
- Autorização do usuário: corrigir temperatura e fazer testes; pedir abertura
  física da porta quando necessário. Não abrir serial em paralelo ao coletor.
- Abrir serial pode reiniciar Uno; houve reinício na conexão inicial e após
  retomar coleta. Salvar aprendizado/estatísticas em EEPROM ainda não implementado.
- CPU: análise de objetos RoomCam desligada via POST `/api/vision/stop`
  com JSON `{}`; vídeo permanece disponível. Só fotos não exigem inferência.
  `roomcamctl vision stop` retornou 404 nesta sessão, usar API se necessário.
- Coletor serial corrigido com `select.select`: de ~100% para ~0,1% CPU.
  Teste com pseudoporta verificou espera ociosa e preservação de bytes.

Acompanhamento inicial após ajuste: referência 36,5 °C às 12:35:40,
36,7 às 12:36:40, 36,8 às 12:37:40 e 36,9 às 12:39:40;
Arduino pareado em 36,83 / 36,95 / 36,89 / 36,95 °C, respectivamente.
Ainda não é comprovação de equilíbrio prolongado nem do teste de porta.
Capturas pareadas em `/tmp/incubadora-telemetria/pos-ajuste-camera/`,
metadados em `observations.jsonl`. Coleta de imagem limitada a uma hora,
sem inferência local de objetos e sem mover PTZ.

## Falha observada e correção da aplicação do PID — 2026-10-27

- Teste solicitado: abertura física de ~30 s, sem mover água/sensores;
  usuário confirmou execução. Modo porta ficou pausado ~57 s: abertura entre
  ms 883662/886129 e fechamento entre 940321/942611 no log pós-calibração.
- Arduino chegou a 33,39 °C após fechar. A referência voltou a 37,0 °C
  às 13:00, mas às 13:04 marcou 37,3 °C; Arduino atingiu 37,51 °C,
  já com aquecedor desligado, e depois caiu a ~36 °C.
  Logo, o primeiro ajuste de offset não resolveu a oscilação. Não declarar
  aquele teste aprovado nem usar somente a passagem por 37,0 como estabilidade.
- Problema encontrado na aplicação: duração do pulso com apenas 3 s de pausa
  torna a potência não linear: 12/(12+3)=80%, 6/(6+3)=67%.
- Nova versão gravada ~13:11: período mínimo de 20 s entre inícios,
  até 17 s ligado (85% longe da meta) ou 12 s (60% perto); Kd de 6.000
  para 18.000 ms/(°C/min). Antiwindup considera o teto ativo de cada faixa.
  Offset permanece +1,575 °C; Kp, Ki, corte de 37,1 e emergência de 39 °C preservados.
- Teste da função C++ real verificou 6 s ligados a cada 20 s durante seis
  períodos: exatamente 30% de tempo ligado, mantendo cortes e pausas.
  Compilação/upload saída 0, 32.166 bytes Flash e 1.012 RAM estática.
- Coleta nova: `/tmp/incubadora-telemetria/coleta-periodo20-20261027.log`;
  imagens/metadados em `periodo20-camera/`. Houve reinício no começo da
  coleta (BOOT_COUNT 6); desconsiderar trecho inicial truncado e confirmar
  continuidade de ms e ausência de novos boots antes de avaliar a estabilidade.
  Verificação física desta versão ainda pendente.

Refinamento ~13:23: removido o teto por faixa de 12 s/60%, que limitava a
aproximação com demanda saturada perto de 36,7 °C. Limite único de 17 s/85%
e integral máxima de 17 s, preservando período de 20 s e Kd de 18.000.
Compilação/upload saída 0: 32.122 bytes Flash / 1.012 RAM estática.
Coleta atual em `/tmp/incubadora-telemetria/coleta-pid-linear-20261027.log`,
quadros em `pid-linear-camera/`. As pastas `pos-ajuste-camera` e
`periodo20-camera` documentam etapas anteriores, não a versão atual.
Validação física do limite único ainda pendente; não declarar estabilidade
pela passagem momentânea por 37 °C. Confirmar boot e continuidade do log.

## Versão PI/D de manutenção — gravada ~13:52 em 2026-10-27

- A versão de teto único ainda oscilou: depois de capturas em 36,9–37,1 °C,
  às 13:44 a referência caiu a 36,2 °C e o Arduino a 36,08 °C.
- Removido o corte total da demanda logo acima de 37,0 °C. O PI/D deve
  equilibrar perdas também levemente acima da meta; corte independente 37,1 °C
  e emergência 39 °C preservados.
- Ganhos atuais e manutenção inicial descritos no topo. A integral não carrega
  com o grande erro da abertura e fica preservada durante a pausa de porta.
- Testes da função real verificam manutenção em 37,05 °C, corte em 37,1 °C,
  retenção de integral ao pausar/retomar e duty de 30% para 6 s/20 s.
  Teste dos botões verifica também retenção de 11 s de integral no toque longo.
- Compilação/upload saída 0: 32.204 bytes Flash / 1.012 RAM estática.
- Usuário confirmou mínimo/máximo zerados e segunda abertura de ~30 s,
  com os toques longos. Essa execução coincidiu com a gravação/reabertura
  da serial: o registro não separa a recuperação da porta do reinício.
  Não pedir nova abertura agora; acompanhar primeiro esta recuperação.
- Coleta atual: `/tmp/incubadora-telemetria/coleta-pi-manutencao-20261027.log`;
  imagens/metadados: `pi-manutencao-camera/`; observador temporário
  `observar-manutencao.py`. Confirmar processos/frescor antes de continuar.
- Início às ~13:53: Arduino 34,33–34,51 °C, referência visual 35,4 °C;
  ambos os controles habilitados. Validação física desta versão ainda pendente.

## Aprendizado somente em temperatura lenta — gravado ~14:19

- A etapa anterior também falhou: pico de 37,64 °C no Arduino e máximo
  visual de 37,2 °C na referência; depois caiu a 36,1 °C na referência.
  O primeiro patamar em 36,9 °C não comprovou estabilidade.
- Integral positiva agora aprende somente com tendência pronta e
  |taxa| <0,05 °C/min, em qualquer distância da meta, com saída não saturada.
  Durante aquecimento/resfriamento rápido, mantém a estimativa de perdas.
  Erro negativo ainda descarrega a integral. Ganhos 9.000/1.000/18.000,
  período 20 s e teto 17 s preservados; PI/D segue ativo até corte 37,1.
- Inicialização e resets usam 10 s/20 s (50%); pausa de porta preserva o valor
  aprendido na RAM. Não há gravação do aprendizado em EEPROM.
- Testes reais verificam aprendizado de perda estacionária em 36,3 °C e
  congelamento da integral com tendência de +0,2 °C/min, além das verificações
  anteriores. Compilação/upload saída 0: 32.234 bytes Flash / 1.012 RAM.
  Restam só 22 bytes de Flash no Uno: recompilar qualquer alteração futura.
- Coleta atual: `/tmp/incubadora-telemetria/coleta-aprendizado-estavel-20261027.log`;
  imagens/metadados: `aprendizado-estavel-camera/`, observador `observar-estavel.py`.
  As demais pastas são ensaios anteriores. Validação física atual ainda pendente.
- Usuário confirmou mais um reset de mínimo/máximo após a gravação desta
  revisão, por volta de 14:22, sem abrir a porta. Usar esse registro para o pico atual.
