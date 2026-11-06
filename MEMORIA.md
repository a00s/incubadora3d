## Revisão final após pico real — gravado em 2026-11-06

- Revisão física autônoma encontrou pico54.790ppm na versãobcf2e8e (déficit inteiro
  sem a correção de espera abaixo). Não ocultar esse resultado nem dizer estável.
- Causa verificada no trace: amostras subiram ainda abaixo da concentração anterior
  à dose; uma reversão isolada em289.628ms liberou37ms extras. O timer do pico só
  memorizava máximos acima daquela concentração e esquecia as subidas desde o vale.
- Corrigido: updateCo2RecentRise guarda a última amostra com subida>2ppm/s durante
  avaliação de uma dose. Mantém graça6s antes de reabrir, mesmo que a amostra seguinte
  caia. Nova máxima real continua renovando espera20s, sem encurtamento. Graça curta
  evita exigir20s extras por qualquer ruído. Preservados mínimo20s, dose pela última
  resposta/déficit inteiro, ganho adaptativo, limites, porta, aquecimento e travas.
- Teste reproduz valores/tempos reais277.211/287.561/289.628ms e agora bloqueia o
  comando37ms; testa expiração6s,20s de pico, nenhum vínculo sem dose e rollover.
  Cinco suites passaram, inclusive20.000histórias numéricas. Build31.532bytes/1.121RAM.
- Upload final scripts/arduino.sh upload --verify, saída0. Coletor antigo102666 foi
  parado por SIGINT antes da gravação, sem comandos para a placa. Nova coleta somente
  leitura SEM timeout, sessão1115:
  /tmp/incubadora-telemetria/co2-ajuste-manutencao-final-20261106.log.
  BOOT_COUNT13; co2_enabled1,heater_enabled1,range_lock0, primeira leitura46.529ppm,
  temperatura36,93°C. Descartar dados anteriores ao BOOT13. Sem ON/OFF/ACK enviados.
- Mais8.104cenários finais (duas sementes, perda/vazão variáveis, partida e duas
  câmaras), além dos12.156intermediários. Válvula com limiar manteve49.348–50.032ppm
  na última hora; antes48.092–49.781. Grade constante final181/400 na faixa versus
 170/400, semente separada171/400 versus157/400. Diversos estresses seguem falhando;
  simulação não é calibração e não prova regulação física. Relatório registra pico
  real intermediário, resultados finais e hashes atuais de ino/header/hex.
- Não foi fixado valor de pressão: ajuste continua pela resposta da última dose.
  Caps de ausência de resposta/partida e teto1000ms permanecem e limitam a faixa
  possível; não prometer gás disponível ou vazão arbitrária. Verificação prolongada
  final de manutenção em5% ainda pendente. Sem alterações CAD.

## Ajuste de manutenção e vazão variável — gravado em 2026-11-06

- Relato: mais contínuo/melhor, mas cai47–48milppm. Usuário pediu ajuste de abertura
  e depois autorizou conduzir revisão/gravação sozinho enquanto dorme, considerando
  a variação da pressão com o enchimento do cilindro.
- Evidência: última hora do log antigo teve1.725amostras, mínimo44.363, mediana46.803,
  máximo50.360ppm. Doses produtivas de11/13ms eram cortadas para5–9ms e só depois
  voltavam a crescer, permitindo queda. São respostas líquidas; não diagnosticar
  vazamento físico exclusivamente com a queda do sensor (mistura também contribui).
- Mudança no firmware é uma linha no header: último tempo × déficit INTEIRO / última
  subida, em vez de metade do déficit. Aumento limitado10% antes do arredondamento,
  redução imediata, aprendizado pela última dose. Preservados20s, espera por subida,
  porta, warmup120s, limites/caps de dose, aquecimento e travas persistentes.
- Pressão: continua usando a resposta nova de cada dose, sem valor de manômetro nem
  ajuste para uma pressão fixa. Ganho menor pede tempo maior, ganho maior reduz
  imediatamente. Caps iniciais/sem resposta e teto1000ms ainda limitam a adaptação;
  não prometer funcionamento com vazão arbitrária ou cilindro sem gás.
- Cinco testes passaram, incluindo20.000histórias e exemplos13ms/2645ppm/deficit2137
  (6ms antigos→11ms novos), ganhos decrescentes/crescentes e gates/porta/rollover.
  Build31.432bytes/1.117RAM. Upload --verify terminou com saída0.
- Coleta somente observação sessão55176, SEM timeout:
  /tmp/incubadora-telemetria/co2-ajuste-manutencao-20261106.log. Abrir serial reiniciou
  o Uno: BOOT_COUNT11; co2_enabled1,heater_enabled1,range_lock0; primeira leitura
 43.876ppm e temperatura36,61–36,80°C durante retomada térmica/warmup. Descartar
  linhas duplicadas anteriores ao BOOT_COUNT11. Sem ON/OFF/ACK enviados.
- Observação USB inicial após warmup: doses62 e69ms em sequência, depois aguardou
  a subida sem novas injeções; leitura40.428→47.136ppm de pico parcial. Atribuição
  individual não é calibração isolada. Ainda não comprova manutenção em5%.
- 12.156cenários modelados8h: comparação antes/depois em duas sementes, grade
  anterior de partida e duas câmaras com maior queda/vazão (hipotéticas). No caso
  de válvula com abertura mínima, mínimo da última hora48.092→49.348ppm e máximo
 49.781→50.032; pico transitório50.889 sem mudança. Grade constante dentro da faixa
  na última hora170/400→216/400; semente separada157/400→200/400. Outros estresses
  continuam falhando (excesso ou nível baixo); não declarar tudo aprovado.
- Evidência, comandos, resultados e hashes de ino/header/hex em
  docs/ensaios/co2_manutencao_2026-11-06.json. Regulação física prolongada pendente.
  Sem alterações CAD; visualizador existente atualizado em/tmp e8081 conferido.

## Última dose como referência — gravado em 2026-11-05

- Decisão explícita do usuário: simplificar, aprender pela última dose, repor quando
  estiver abaixo e cair/estabilizar; esperar enquanto sobe; intervalo mínimo20s.
  Usuário autorizou gravação novamente (“manda”).
- Implementado em firmware/incubadora/co2_dosing.h: tempo anterior × metade do
  déficit / maior subida líquida desde a dose; aumento limitado10%, redução imediata.
  Resposta<50ppm aumenta10% sem divisão e sem reset. Sem resposta há teto por
  déficit/150, permitindo até pelo menos80ms depois da primeira tentativa; limites
  gerais5–1000ms. Não soma doses, não usa Padé nem espera adaptativa90–600s.
- Gate real:20s desde fim da injeção,20s sem novo pico, histórico válido, inclinação
  <=50ppm/min e subida recente<=2ppm/s (tolerância ao ruído). Contador30ciclos e
  flag de estabilidade antigos ficam na telemetria, mas não bloqueiam o automático.
  Warmup120s, porta, leitura inválida, cortes e EEPROM continuam preservados.
- Verificado: cinco testes C++ locais passaram, incluindo20.000 histórias numéricas,
  gate exato20s, platô sem precisar cair, subida recente mesmo com média negativa,
  porta, falha, rollover, aquecimento e visor. Build31.444bytes/1.117RAM.
- Upload scripts/arduino.sh upload terminou com saída0 e --verify. Coletor somente
  leitura sessão1377: /tmp/incubadora-telemetria/co2-ultima-dose-20261105.log.
  BOOT_COUNT9; CO₂ habilitado1, aquecimento1, trava0, temperatura36,86–37,05°C,
  leitura inicial41.202ppm caindo durante warmup. Nenhum ON/OFF/ACK enviado.
- 6.063 simulações exploratórias de8h, duas sementes, uma/duas câmaras, partida
 2.000/45.000ppm, porta, pressão, sensor e contato. Os quatro casos de curva medida
  na planta de uma câmara ficaram entre49.879 e50.053ppm de pico; na planta de duas
  câmaras a concentração no sensor difere da principal e alguns picos passam51.000.
  As grades amplas ainda têm excessos e recuperação insuficiente: NÃO afirmar todos
  aprovados nem regulação física estável. Relatório/hashes de fonte/header/hex:
  docs/ensaios/co2_recuperacao_2026-11-05.json. Validação física prolongada pendente.
- Sem alterações CAD; visualizador existente copiado para/tmp e porta8081 conferida.

## Auditoria do simulador e duas câmaras — 2026-11-05 (estado mais recente)

- Relato físico do usuário: resposta inicial pode demorar mais com CO₂ muito baixo,
  na retomada ou após porta aberta, devido à mistura/renovação no misturador e na
  câmara principal. Tratar como relato; volumes efetivos e tempos não calibrados.
  CAD/README documentam sensor no misturador e canal Ø6,2 até a câmara.
- Correção verificada no simulador: atraso zero agendava gás em posição da fila já
  consumida e perdia a dose. Agora entrega no próximo passo (discretização até2s).
  Teste de conservação falha ao restaurar o bug e passa com a correção.
- Tendência/janela de estabilidade passaram a usar o bloco real do firmware;
  histórico reinicia na falha de sensor. Dois tanques opcionais têm concentrações
  separadas, entrada/deslocamento de gás puro e troca conservativa entre volumes.
  Conferidos conservação da troca, entrada zero e limite de gás puro.
- 8.084 cenários exploratórios: uma/duas câmaras, atraso máximo30/300s,
  volumes relativos supostos10%/50%, duas sementes e partida2.000/45.000ppm.
  Resultados/hipóteses/hashes: docs/ensaios/co2_auditoria_simulacao_2026-11-05.json.
  Há excessos em parte dos testes de estresse; NÃO declarar aprovação física.
  O número82.805ppm citado ao usuário veio de atraso hipotético284s, não medido.
- Telemetria preservada: boot5, doses96/122/144ms tiveram subida líquida>=50ppm
  após aproximadamente29,4/10,5/8,5s e picos94,0/77,1/87,6s. Tempos contados desde
  DATA anterior ao pulso (~uma amostra de incerteza). Não equivalem a calibração
  isolada. Doses seguintes e boot7 sem subida líquida; causa não determinada.
- Nenhum upload nesta auditoria. Última gravação confirmada anteriormente foi a
  matemática com proteção de perda de resposta,32.252bytes/1.125RAM. A USB não foi
  aberta agora e estados atuais não foram inferidos. Sem comandos ON/OFF/ACK.
- Firmware candidato NÃO gravado ainda está no diretório de trabalho: mínimo20s
  no gate, mas contador legado30ciclos (~60s) e estabilidade30s continuam limitando
  o automático. Não afirmar que já executa a lógica solicitada de20s/platô.
  Compilação32.250bytes/1.125RAM e cinco testes locais passaram; testes não provam
  estabilidade. Falta ajustar platô e atribuição de doses ainda não observadas.
- Alterações anteriores de firmware/README/testes continuam pendentes no diretório;
  commit desta auditoria contém simulador, relatório e memória. Sem alteração CAD.
  Visualizador copiado para/tmp e servidor8081 respondeu200.

## Recuperação lenta desde~2.000ppm — revisão em bancada 2026-11-05

- Relato novo: CO₂ habilitado na tela normal, após~10min ainda~2.000ppm; usuário
  reconectou USB para revisão/teste. Não é continuação presumida da trava anterior.
- Verificado na USB antes da gravação: leitura válida~1.950ppm,co2_enabled1,
  co2_range_lock0; último pulso20ms sem subida útil. Coleta abriu/reiniciou placa;
  firmware antigo depois emitiu5ms e continuou sem subida. O teste anterior só
  media picos/última hora e começava em45.000ppm: omitia partida realmente baixa.
- Comparação pelo mesmo modelo, semente e planta: desde2.000ppm, nominal antigo
 12.436s→novo2.962s; válvula com tempo morto20ms13.874s→3.208s; vazão alta
 5.054s→2.516s. Isso é simulação (até~50min no nominal modelado), não promessa
  de tempo físico nem prova de solução. Baixa pressão/perda elevada ainda lentas.
- Revisão gravada com --verify e saída0:32.226bytes flash/1.121RAM. Cinco testes
  reais C++ passaram. Sem mudanças no controle térmico, cortes ou trava de faixa.
- Partida sem dose anterior não espera300s além do warmup120s. Abaixo40.000ppm,
  sonda40ms, progressão fraca+20ms e com ganho pode dobrar; >=40.000ppm mantém
  sonda5ms/crescimento5ms. Dose sempre limitada a metade do déficit (1/3 perto).
  Resposta positiva pode reduzir dose mesmo com ganho ainda não validado.
- Somente abaixo40.000ppm, observação pode encurtar para>=90s após subida>=200ppm,
  taxa<=0 e pico sem aumentar há30s. Ausência de resposta mantém300s. Retomada da
  porta/religamento invalida validação anterior e faz nova sonda na faixa atual.
- Removido cálculo de atraso adaptativo que desde a última revisão não era usado
  para decidir espera/dose. Espera de recuperação agora usa a condição real acima.
- Simulações ampliadas:2 grades×2.000 casos (45.000 e2.000ppm),15 casos nomeados
  por grade; comparação com versão a41da6b. Planta de porta agora pausa30s e zera
  duração anterior na retomada como o firmware real. Dois excessos nos1.600 casos
  sinalizados de cada grade; trocas sem pausa têm mais excessos. Muitos casos
  de perda/vazão insuficiente continuam baixos. Todos resultados/limites em
  docs/ensaios/co2_recuperacao_2026-11-05.json; não declarar tudo aprovado.
- Coleta nova somente observação, SEM timeout, sessão77612:
  /tmp/incubadora-telemetria/recuperacao-pos-correcao-20261105.log, BOOT_COUNT3.
  Primeira dose40ms em122.148ms; até261.016ms leitura~1.893ppm, sem subida útil.
  Aguardando próxima dose60ms e resposta; usuário confirmou cilindro/regulador
  abertos, gás e pressão disponíveis. Valor numérico não informado nem exigido
  pelo algoritmo; controle aprende pela resposta, não pelo manômetro.
  Não diagnosticar só software nem afirmar válvula abriu: confirmou-se comando.

## Gravação final confirmada — 2026-11-05

- `scripts/arduino.sh upload` fora do sandbox terminou com saída0 e `--verify`;
 32002bytes flash/1121RAM. Cinco testes de regressão passaram.
- Serial após gravação: BOOT_COUNT3; evento
  `co2_range_lock_restored_after_boot`. DATA:co2_enabled0,heater_enabled1,
  valve_open0,co2_range_lock1; temperatura36,74–36,86°C nos primeiros segundos.
  CO₂ bruto~2290ppm, porém co2_valid0 e sensor em aquecimento: NÃO interpretar
  como concentração física confirmada nem como permissão para destravar.
- Trava persistente preservada, sem CO2 ACK, CO2 ON ou HEAT ON enviados.
  Leitor serial somente observação, sessão13159; verificar se segue vivo antes
  de reutilizar USB. Abrir serial reiniciou a placa. Validar com medição externa
  antes de liberar trava; não declarar regulação física aprovada.

## Revisão ampliada e simulação — 2026-11-05

- Usuário autorizou gravação e pediu milhares de simulações, incluindo troca de
  cilindro e porta. Upload da revisão anterior4381627 retornou saída0 fora do
  sandbox; a placa só é acessível fora do isolamento. Revisão final conferir abaixo.
- Revisão atual: sondas/mínimo5ms; crescimento máximo5ms; espera300s inclusive
  na porta; tendência<=50ppm/min por30s. Ganho maior imediato, menor1/3 por resposta;
  dose de metade do déficit (1/3 perto da meta). Teto1000ms preservado.
- Desligar/religar CO₂, retomar porta, dez minutos sem dose ou falha de sensor
  exigem nova sonda5ms. Falha de sensor reinicia espera300s para não empilhar dose
  cuja resposta ficou invisível. Trocar cilindro usando pausa/desligamento do CO₂;
  sem sinalização, primeira dose ainda pode usar ganho antigo e causar excesso.
- Simulador `scripts/simulate_co2_control.py` extrai seleção de pulso e gates reais
  C++; planta hipotética varia vazão, perda, atraso0–300s, mistura10–120s, ruído,
  falha180s, tempo morto da válvula0–20ms, porta e troca. Semente20261105;
  2.011 cenários de8h (16.088h modeladas). Não é ensaio físico nem calibração.
- Resultado verificado da grade2.000: em1.600 casos sem troca não sinalizada,
  dois picos>51000 (máx51356ppm). Em400 trocas sem pausa,36 excessos. Muitos
  casos de perda alta/vazão insuficiente ficaram abaixo49000. Não declarar todos
  cenários aprovados ou estabilidade física. Relatório com hash e parâmetros:
  `docs/ensaios/co2_simulacoes_2026-11-05.json`. Modelos de casos conhecidos e
  limites de pulso/espera têm asserções; grade exploratória registra falhas.
- Sem alterações CAD. O visualizador foi copiado para/tmp e respondeu200 na8081
  durante a etapa anterior. Não liberar trava de faixa nem forçar controles ON.

## Correção de dosagem CO₂ — 2026-11-05

- Relato: usuário trocou por cilindro com mais CO₂; houve excesso e alerta/parada
  durante a noite. Atribuição ao aumento de vazão é hipótese consistente com o
  relato; não há telemetria desta noite disponível nesta sessão.
- Código verificado: permitia repetir dose em 60 s, compensar perdas projetadas e
  usar todo o déficit na recuperação. Ganho maior era diluído na estimativa antiga.
- Correção local: espera mínima180 s entre doses automáticas, inclusive recuperação;
  usa metade do déficit medido (1/3 perto da meta), sem projetar perdas para dosar.
  Ganho maior é adotado imediatamente; ganho menor decai1/3 por resposta, seguindo
  esvaziamento gradual. Após10min sem dose volta à sonda20ms. Crescimento máximo
 20ms por dose e teto1000ms mantidos; cortes e trava persistente preservados.
- Limitação: sem medição de pressão, a primeira dose após troca durante dosagem
  contínua ainda usa informação anterior. Sonda mínima20ms também exige validação
  com a pressão nova; não afirmar que impede todo excesso.
- Compilação verificada:31892bytes flash,1121RAM. Testes de controle, ganho,
  recuperação da porta, perdas, térmico e visor executados. Sem porta ttyACM nesta
  sessão: NÃO gravado, NÃO retomado controle físico, NÃO validado no cilindro novo.
- Sem alteração CAD ou de peças; STL/STEP/3MF e visualizador preservados.

# Memória local do projeto

## Trabalho ativo — controle térmico e visor, 2026-10-27

Atualização10:26 de28/10: PAUSA explícita solicitada pelo usuário para
colar novamente o metal da porta que se descolou (relato físico). Log
EVENT,door,open, ambos controles0; ALL OFF enviado para confirmar pausa.
Não reativar aquecimento/CO₂ até usuário retomar. Coletor segue ativo.
Supervisor anterior cortou04:21:06 em37,24 °C, perdendo continuidade
noturna. Usuário esclareceu que não quer interrupções experimentais
no computador. `scripts/supervise_temperature.py` agora SOMENTE LEITURA,
sem acesso serial, sem limite térmico/tempo e sem HEAT OFF no encerramento.
Teste com log sintético38 °C e SIGTERM confirmou registro sem desligamento.
Monitor atual sessão87853, estado `observacao-sem-corte.json`, mesmo log
co2-adaptativo. Firmware permanece igual, com corte normal37,1 e emergência39.
Tentativa HEAT ON10:25 foi recusada ERR,DOOR_OPEN; não foi reativado.


Retomada verificada01:20: upload com verificação saída0, BOOT36 após
reabrir coleta. Log atual `/tmp/incubadora-telemetria/coleta-co2-adaptativo-20261028.log`,
SEM timeout; sessão66366. Supervisor contínuo sessão93438, estado
`supervisao-co2-adaptativo.json`, `duration_limit_seconds=null`; ACK HEAT ON
e ambos controles1 confirmados. Temperatura32,61 °C, CO₂~32317ppm.
Câmera ligada ao log NOVO via `observar-co2-adaptativo.py`, sessão91851,
pasta `co2-adaptativo-camera/`; observador antigo parado para não parear
imagens atuais com log velho. Warmup CO₂2min após boot; resposta dos
pulsos >80ms precisa validação física. Metadados/hash em
`docs/ensaios/co2_adaptativo_2026-10-28.json`. Não reintroduzir prazo de
1h no aquecimento nem prazo12h no coletor por padrão.


Atualização01:20 de28/10: usuário pediu aquecimento indefinido SEM limite
de duração; não reintroduzir timeout1h. Supervisor antigo efetivamente
desligou HEAT01:02, não por temperatura. Novo script versionado
`scripts/supervise_temperature.py` sem prazo; conserva corte experimental
37,2 °C e falta de dados. Remover wrapper `timeout` interrompeu coletor,
causando pausa adicional; coleta restabelecida SEM timeout e BOOT34.
Usuário observou CO₂ baixo e suspeita cilindro quase vazio (relato/hipótese).
Verificado: meta50000ppm, leitura~31750ppm, pulsos repetidos80ms; código
limitava toda adaptação a80ms. Correção: teto1000ms, crescimento máximo
20ms por dose também com ganho validado; redução imediata pelo déficit
permitida. Sonda inicial20ms, esperas/intertravamentos preservados.
Cinco testes passaram e build32186bytes flash/1121RAM. Gravação/retomada
conferir abaixo e no log novo. Não atribuir baixa concentração só ao cilindro;
resposta física à correção ainda não validada.


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
