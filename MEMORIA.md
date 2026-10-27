# Memória local do projeto

## Trabalho ativo — controle térmico, 2026-10-27

Atualização 27/10 ~15:48: usuário confirmou câmara SEM células e autorizou
ensaios automáticos. A revisão anterior foi REPROVADA: Arduino chegou a
37,51 °C ~15:09, mesmo com saída desligada, por calor residual. Não atribuir
esse pico à diferença entre sondas. Evidência completa em docs/ensaios.

Revisão atual gravada e verificada ~16:58: meta 37 °C, previsão de 90 s
corta saída se temperatura + taxa positiva × 1,5 min atingir 37,1 °C.
Retoma automaticamente; controles permanecem habilitados. Corte por leitura
real 37,1 °C e emergência travada 39 °C. Sem tendência inicial usa manutenção.
Horizonte 180 s e previsão contra 37,0 °C ficaram abaixo da meta; mesmo
90 s contra 37,0 °C manteve ~36,8 °C. Ensaios arquivados separadamente em
docs/ensaios/antecipacao180_2026-10-27.* e antecipacao90_2026-10-27.*.
A tolerância de aprendizado foi corrigida de 0,05 para 0,15 °C/min:
um passo de 0,0625 °C em 30 s produz 0,125 °C/min. O limite antigo
bloqueava 78% das amostras elegíveis. Mantidos anti-saturação, bloqueio
na previsão de excesso e durante subida rápida. Teste novo cobre esse passo.
A etapa anterior teve máximo 37,14 °C e média abaixo da meta; arquivada
em docs/ensaios/antecipacao-limite_2026-10-27.*.
Resultado físico da revisão atual ainda PENDENTE, não declarar corrigido.
Testes de software de controle térmico passaram; demais testes passaram na
revisão anterior sem mudanças em CO₂/porta/display.

Pedido do usuário: visor da câmara agora mostra DUAS casas decimais,
com cache em centésimos; temperatura interna continua com uma. Formatação
compartilhada preserva a perda de CO₂; teste cobre centésimos, negativos,
NaN, limites de tela e modo porta. Gravado com verificação. Controle térmico
não mudou nesta gravação; etapa anterior arquivada como parcial, pico37,14.
Preparação de recuperação começou ~16:58 com aquecimento OFF e CO₂ ON.
Primeiro supervisor abortou ANTES de enviar HEAT ON: temperatura residual
ultrapassou a pré-condição 37,1 °C (~17:00), pico no log 37,20 °C ainda
com saída desligada. Não chamar esse trecho de recuperação aprovada.
Supervisor inicial terminal: supervisao-recuperacao-centesimos.json.
Às ~17:03 iniciou supervisor novo, sem reabrir serial/regravar: espera
20 s de dados contínuos e temperatura <=36,5 °C antes de HEAT ON.
Depois vigia pico, abortando a 37,2 °C ou falha de telemetria. JSON atual
supervisao-recuperacao-retomada.json; processo supervisionar-recuperacao-retomada.py.
Não reiniciar processos apenas porque uma consulta demora; conferir PID e estado.
Retomada confirmada por ACK e dados contínuos às 17:03:54. Após religar,
Arduino ainda caiu até ~35,6 °C, por atraso térmico, e começou a subir.
Às ~17:13 chegou a 36,83 °C; referência em 36,4 °C na captura 17:12:45.
Não ajustar offset durante essa transição. Ensaios continuam com CO₂ ON.
Imagens recortadas e comparação visual em docs/ensaios/camera_recuperacao_*.jpg
e referencia_recuperacao_2026-10-27.csv. Validar pico e patamar antes de encerrar.
Não regravar agora: observar esta recuperação e a manutenção posterior.

Coleta atual: /tmp/incubadora-telemetria/coleta-recuperacao-centesimos-20261027.log;
fotos em recuperacao-centesimos-camera; supervisor atual em supervisao-recuperacao-retomada.json.
CO₂ mantido ATIVO por pedido do usuário. Supervisor externo interrompe
apenas aquecimento a 37,2 °C ou perda de telemetria; não confundir esse
aborto experimental com o corte normal que retoma sozinho.
Conferir processos vivos e último BOOT antes de assumir continuidade.
Não reabrir serial durante ensaio. Não pedir abertura da porta nesta etapa.
Não declarar estabilidade nem liberar uso com células sem medir resposta completa.
CAD e peças não modificados; visualizador regenerado e servido em 8081.

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
- Meta 37,0 °C; offset aplicado na aquisição `+1.575 °C` (ajustado e gravado em 2026-10-27;
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
  A integral cresce só com tendência pronta, |taxa| <0,05 °C/min e saída não saturada;
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
