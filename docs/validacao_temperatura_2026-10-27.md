# Ajuste térmico — 27 de outubro de 2026

## Montagem e objetivo

Meta de 37,0 °C na referência junto à região das amostras. Segundo o usuário,
a sonda de referência está apoiada na gaveta metálica; a DS18B20 do Arduino
fica pendurada livre no teto, aproximadamente 3 cm distante. A referência
recebe influência do metal e a DS18B20 responde ao ar. Não é uma calibração
intrínseca da sonda nem uma validação da uniformidade de toda a câmara.

O reservatório anterior foi substituído por placa de Petri mais baixa e
com maior superfície. Volume de água não informado. Manter a montagem
durante a comparação; alterações de água, contato e posição podem mudar
o desvio entre as leituras.

## Evidência anterior e alteração

Entre 12:24 e 12:28, a câmera mostrou 36,2–36,3 °C na referência. O Arduino,
na última hora anterior ao ajuste, apresentou média de 36,9707 °C,
mínimo de 36,76 e máximo de 37,14 °C, com o offset anterior de +2,325 °C.

Foi aplicada uma redução inicial de 0,75 °C no offset, para **+1,575 °C**.
Reduzir a leitura corrigida faz o controle aquecer mais até atingir a meta;
o efeito físico deve ser conferido após o equilíbrio.

Nessa primeira etapa não foram alterados ganhos PID, limites de pulsos,
lógica de CO₂ ou cortes por falha e sobretemperatura. O teste abaixo mostrou
que corrigir só o offset era insuficiente.

## Verificações de software e gravação

- `scripts/test_heater_control.py`: calibração no ponto observado, limites
  de pulsos, pausa mínima, leitura inválida e emergência.
- `scripts/test_door_recovery.py`: pausa/restauração pelo toque longo,
  persistência e isolamento dos cliques curtos.
- `scripts/test_co2_control.py`, `test_co2_loss.py` e
  `test_display_door.py`: verificações existentes aprovadas.
- `scripts/arduino.sh compile` e `upload`: saída 0; 32.128 bytes de Flash
  e 1.012 bytes de RAM estática no Uno. Gravação em torno de 12:30.

## Observações físicas

[Leituras pareadas em CSV](validacao_temperatura_2026-10-27.csv). Os horários
são os da captura no computador, com fuso. A câmera estava em streaming,
com quadro fresco. A leitura da referência foi feita visualmente no visor
principal; não foi inferida automaticamente por OCR.

Na subida após a gravação, a referência passou de 36,2 °C às 12:32:40
para 36,9 °C às 12:39:40 e 37,0 °C às 12:41:40, repetindo 37,0 °C
às 12:42:40. As diferenças durante a subida não devem ser usadas para
reajustar continuamente a calibração.

O usuário confirmou o teste solicitado de abertura física de ~30 segundos.
O modo porta ficou pausado por aproximadamente 57 segundos: transição de
abertura entre ms 883662/886129, fechamento entre 940321/942611, medidos
desde o boot no log pós-calibração. Não confundir o tempo de pausa do botão
com o tempo exato de abertura física.

O Arduino chegou a 33,39 °C após retomar; a referência voltou a 37,0 °C
às 13:00. Porém às 13:04 a referência atingiu 37,3 °C e o Arduino chegou
a **37,51 °C**, 114,6 segundos após a última amostra com aquecedor ligado.
Depois, o Arduino voltou a ~36 °C. **O teste da primeira etapa falhou:
não houve estabilidade apenas com a correção de calibração.**

## Segunda etapa: aplicação proporcional da potência

O PID antigo regulava a duração ligada e mantinha apenas uma pausa mínima
de 3 s. Isso resulta em potência não linear: 12 s ligados / 15 s totais =
80%; 6 s / 9 s = 67%. Reduzir a demanda pela metade diminuía pouco a
potência média, o que prejudica o ajuste do PID em milissegundos.

Nova versão gravada em torno de 13:11:

- Pelo menos 20 s entre os inícios dos pulsos: 6 s significam 30% de
  tempo ligado, desde que haja demanda contínua e nenhum corte antecipado.
- Máximo 17 s ligado longe da meta (85%) ou 12 s perto (60%), preservando
  pelo menos 3 s desligado. Pulsos podem ser encurtados imediatamente.
- Kd de 6.000 para 18.000 ms/(°C/min), aproximadamente 60 s de antecipação
  relativamente ao proporcional de 18.000 ms/°C. Kp e Ki preservados.
- Antiwindup considera o teto ativo, 17 ou 12 s, em vez de bloquear a
  integral sempre que a demanda passava de 12 s, mesmo em recuperação.
- Offset de +1,575 °C, lógica de CO₂, corte de 37,1 °C e emergência de
  39 °C preservados. Não foi implementado aprendizado em EEPROM.

Teste da função C++ real verificou seis períodos com demanda de 6 s:
36 s ligados em 120 s totais, exatamente 30%, além dos testes de
antecipação pela tendência, limites e segurança. Os outros quatro testes
do firmware também passaram. Compilação e upload: saída 0, 32.166 bytes
de Flash e 1.012 de RAM estática.

Refinamento em torno de 13:23: o teto de 12 s/60% perto da meta foi
retirado. A aproximação estava lenta perto de 36,7 °C com demanda atingindo
esse teto, e a faixa reduzida limitava a potência disponível nessa região.
A versão atual usa **um único teto de 17 s/85%**, também para a integral,
sem limiar de temperatura para alternar tetos. Período de 20 s, pausa de
3 s e Kd de 18.000 preservados. Compilação/upload saída 0: 32.122 bytes
Flash / 1.012 RAM estática. O teste de função C++ passou novamente.

**Estabilidade física da versão com teto único ainda em acompanhamento.**
Leituras dessa versão em [CSV separado](validacao_pid_linear_2026-10-27.csv).
Nas capturas verificadas entre 13:34 e 13:42, a referência ficou em
36,9–37,1 °C. O Arduino teve pico de 37,33 °C e voltou a baixar; a leitura
de referência das 13:40 foi 37,1 °C e a das 13:42 foi 37,0 °C.
Essa observação corresponde à porta fechada. O teste de porta com a
versão atual foi solicitado e ainda não consta no log; o teste anterior
foi feito antes dessas alterações no PID.

Continuação: às 13:44, a referência caiu para 36,2 °C e o Arduino para
36,08 °C. **O patamar anterior não comprovou estabilidade: a versão com
teto único também continuou oscilando.**

## Terceira etapa: PI/D com potência de manutenção

Versão gravada em torno de 13:52:

- PI/D permanece ativo levemente acima de 37,0 °C, mantendo o corte
  independente de 37,1 °C. O corte total na primeira leitura acima da
  meta interrompia também a compensação das perdas, favorecendo a queda
  seguinte antes da resposta do aquecedor.
- Kp 9.000 ms/°C, Ki 1.000 ms/(°C·min), Kd 18.000 ms/(°C/min).
  A relação D/P equivale a aproximadamente 120 s, próxima dos 114,6 s
  entre a última amostra ligada e o pico observado na primeira etapa.
- Manutenção inicial de 10 s/20 s (50%), baseada no histórico de 50–60%
  observado. O PI ajusta a manutenção; a integral positiva cresce com
  erro menor que 0,5 °C e saída não saturada, sem carregar com o grande
  erro frio da abertura. Erro negativo descarrega a integral.
- A pausa da porta preserva a integral na RAM. Desligamento manual,
  leitura inválida e emergência a reinicializam. Não há gravação do
  aprendizado na EEPROM.
- Teto único de 17 s/20 s, pausa mínima de 3 s, lógica de CO₂ e emergência
  de 39 °C preservados.

Testes das funções reais verificam potência de manutenção em 37,05 °C,
corte em 37,1 °C e preservação de 11 s de integral na pausa/retomada,
inclusive pelo toque longo dos botões. Os cinco testes do firmware passaram.
Compilação/upload saída 0: 32.204 bytes Flash / 1.012 RAM estática.

O usuário informou mínimo/máximo zerados e segunda abertura de ~30 s,
com os dois toques longos. A execução coincidiu com a gravação e reabertura
da serial; esse ensaio combina abertura e reinício, sem separar seus efeitos.
A nova coleta começou às ~13:53 com Arduino 34,33–34,51 °C e referência
35,4 °C, controles habilitados. **Recuperação física ainda em acompanhamento.**

Continuação dessa etapa: a referência atingiu 37,2 °C, e o pico completo
registrado no Arduino foi 37,64 °C; a referência depois caiu a 36,1 °C.
Logo, também não foi aprovada como controle estável. A integral havia
crescido durante a recuperação, aprendendo o transiente como manutenção.

## Quarta etapa: aprendizado em temperatura lenta

Gravada em torno de 14:19. Ganhos 9.000/1.000/18.000, período de 20 s,
teto de 17 s, PI/D nos dois lados da meta e cortes preservados.
A integral positiva agora aprende somente com tendência pronta e
|taxa| <0,05 °C/min, com saída não saturada, em qualquer distância da meta.
Durante variações rápidas, mantém a estimativa de perdas. Erro negativo
continua descarregando a integral. Inicialização e resets restauram 50%;
a pausa da porta preserva o valor aprendido na RAM.

Testes reais verificam aprendizado de uma perda estacionária em 36,3 °C,
congelamento da integral durante tendência de +0,2 °C/min, manutenção,
pausa da porta e cortes. Compilação/upload saída 0: 32.234 bytes Flash /
1.012 RAM estática. O usuário confirmou novo reset do mínimo/máximo
depois dessa gravação, por volta de 14:22, sem abrir a porta.
**Verificação física dessa revisão ainda em andamento.**

Leituras pareadas desta revisão em
[CSV](validacao_aprendizado_estavel_2026-10-27.csv). A revisão completa dos
quadros identificou uma leitura de **37,2 °C às 14:35:59**, que não apareceu
na amostragem visual inicial. Portanto, não considerar 37,1 °C como máximo
de todo o arranque. De 14:36:59 até 14:47:59, todos os quadros por minuto
verificados ficaram entre 36,9 e 37,1 °C. Às 14:47:59, referência 37,1 °C
e Arduino 36,89 °C. O teste final de porta foi solicitado, com firmware
mantido na mesma revisão; ainda não foi registrado evento de abertura nesse log.

A [telemetria completa desta revisão](ensaios/controle_termico_2026-10-27.csv)
e seus [metadados](ensaios/controle_termico_2026-10-27.json) foram arquivados
no projeto. O arquivo inclui as amostras após o último boot; o estado de
validação permanece pendente do teste isolado de porta. As capturas pareadas
estão no CSV de leituras visuais citado acima; os quadros originais continuam em `/tmp`.

Visualizador regenerado e comparado: malha e layout equivalentes aos anteriores,
sem alterações de CAD/STL/STEP/3MF. Cópia servida atualizada e HTTP 200 na porta
8081; o SHA-256 do conteúdo HTTP coincide com `index.html` servido.

O trecho inicial truncado da nova coleta é descartado; usar as amostras
contínuas após `BOOT_COUNT,6` na etapa com teto de 60%, e após
`BOOT_COUNT,8` na etapa atual. Verificar continuidade e ausência de novos boots.

## Coleta e limites

Logs completos e capturas de diagnóstico ficam em
`/tmp/incubadora-telemetria/`; esse armazenamento é temporário.
Imagens pareadas e metadados: `pos-ajuste-camera/observations.jsonl`.
Log posterior ao ajuste: `coleta-pos-ajuste-20261027.log`.
Log da segunda etapa: `coleta-periodo20-20261027.log`; imagens e metadados
em `periodo20-camera/`.
Versão com teto único: `coleta-pid-linear-20261027.log`, imagens e metadados
em `pid-linear-camera/`.
Versão atual de manutenção: `coleta-pi-manutencao-20261027.log`, imagens e
metadados em `pi-manutencao-camera/`.
Revisão atual: `coleta-aprendizado-estavel-20261027.log`, imagens e
metadados em `aprendizado-estavel-camera/`.

A análise de objetos do RoomCam foi desligada, mantendo o vídeo e as
capturas. O coletor serial passou a esperar dados com `select`, sem
ocupar uma CPU inteira. Testes com pseudoporta verificaram espera ociosa,
preservação do texto e extração de quadros binários MH-Z16.

As verificações de software não comprovam desempenho térmico, precisão
absoluta dos termômetros, temperatura do líquido ou uniformidade espacial.
Nenhuma peça CAD ou configuração do projeto de impressão foi alterada.

## Revisão de antecipação, 16:29

O ensaio anterior com aprendizado estacionário também falhou: Arduino atingiu
37,51 °C ~15:09, com calor residual após desligamento da saída. Pulsos de
identificação estão arquivados em `docs/ensaios/pulso-*.json`.

Foi gravada previsão de 180 s, mantendo corte normal 37,1 °C e emergência
travada 39 °C. O ensaio de 15:44:55 a 16:28 teve máximo 37,01 °C, mas
ficou longamente abaixo da meta; chegou a cortar em 36,58 °C com taxa
0,16 °C/min. Às 16:14 a câmera mostrava referência 36,0 °C e Arduino
36,51 °C. Isso não valida calibração nem estabilidade.

Após solicitação do usuário, previsão reduzida a 90 s e gravada com verificação.
Demais ganhos/cortes mantidos, CO₂ ativo. Nova coleta `coleta-antecipacao90-20261027.log`,
quadros `antecipacao90-camera/`; ambos sob `/tmp/incubadora-telemetria`.
Supervisor externo interrompe somente o aquecimento a 37,2 °C ou falha de
telemetria; esse limite é do ensaio vazio, não emergência do firmware.
Todos os cinco testes de controle passaram; resultado físico ainda pendente.

### Previsão contra o limite, 16:38

O primeiro ensaio de 90 s também permaneceu abaixo da meta: após startup,
Arduino ~36,8 °C e cortes preditivos em 36,83 °C. Máximo total 37,01 °C,
sem leituras acima de 37,1. Telemetria e parâmetros arquivados em
`docs/ensaios/antecipacao90_2026-10-27.*`; etapa de 180 s também arquivada.

Alterada somente a comparação preditiva: previsão de 90 s protege 37,1 °C,
enquanto PI/D continua buscando 37 °C. Corte pela medição real permanece
37,1 °C. Compilação, teste térmico e gravação verificada passaram. CO₂ ativo.
Nova coleta `coleta-antecipacao-limite-20261027.log`, imagens em
`antecipacao-limite-camera/`. Validação física ainda pendente.

### Aprendizado compatível com a resolução, 16:50

Previsão de 90 s contra 37,1 °C chegou à meta e teve máximo 37,14 °C
(uma amostra acima de 37,1), mas média de 36,87–36,92 °C nos trechos
de cinco minutos. Não aprovado como manutenção da meta. Arquivo separado
`docs/ensaios/antecipacao-limite_2026-10-27.*`.

Identificada incompatibilidade: DS18B20 12 bits varia em passos de 0,0625 °C;
em 30 s isso equivale a 0,125 °C/min, acima do limite de aprendizado
de 0,05 °C/min. Na coleta, só 41/187 amostras termicamente elegíveis
passavam esse limite; com tolerância 0,15, 142/187 passariam.
Alterada somente essa tolerância; previsão, cortes, ganhos e CO₂ mantidos.
Teste de regressão novo verifica aprendizado com taxa 0,12 °C/min abaixo
da previsão de corte, sem aprender na subida rápida 0,2 °C/min.
Compilação e gravação com verificação passaram. Nova coleta:
`coleta-aprendizado-resolucao-20261027.log`, fotos em `aprendizado-resolucao-camera/`.
Ensaio físico ainda pendente. Manter esta revisão por vários ciclos antes
de concluir convergência ou necessidade de outro ajuste.

### Visor em centésimos e recuperação automática, 16:58

A pedido do usuário, temperatura da câmara no visor passou a duas casas
decimais, com cache também em centésimos. Campo comporta 37.08 C e
-37.08 C, e leitura inválida mostra --.-- C. Temperatura interna e perda
de CO₂ mantêm uma casa. Teste verifica atualização 37.01 → 37.08,
negativos, NaN e isolamento do modo porta. Controle térmico preservado.

Etapa anterior arquivada como parcial em
`docs/ensaios/aprendizado-resolucao_2026-10-27.*`: máximo37,14 °C,
últimos três minutos ~36,97 °C de média antes da mudança de visor.
Não equivale a validação prolongada. Gravação verificada concluída.

Ensaio novo mantém CO₂ ativo e deixa aquecimento desligado 180 s antes de
retomar automaticamente, para medir recuperação após resfriamento sem abrir
a porta. Esse ensaio não substitui teste físico de abertura. Log
`coleta-recuperacao-centesimos-20261027.log`, fotos `recuperacao-centesimos-camera/`,
supervisor `supervisao-recuperacao-centesimos.json`, todos sob
`/tmp/incubadora-telemetria`. Resultado físico pendente.

Preparação interrompida ~17:00 antes de HEAT ON: subida residual atingiu
37,20 °C no Arduino, com aquecimento desabilitado e saída OFF em todo o
trecho. Referência 37,1 °C na captura ~17:00:54. Isso permanece como
evidência de calor residual; não declarar estabilidade pela etapa curta.
A pré-condição do supervisor abortava ao ultrapassar 37,1 °C durante o
resfriamento. Supervisor novo ~17:03 mantém aquecimento OFF até <=36,5 °C
e 20 s sem reboot, então retoma; limite de aborto em aquecimento continua
37,2 °C. Firmware, leitor serial e câmera mantidos. Registro atual em
`supervisao-recuperacao-retomada.json`; coleta e fotos continuam nos mesmos arquivos.

Retomada confirmada às 17:03:54, sem reinício da serial/placa. O Arduino
ainda caiu até ~35,6 °C após religar; depois recuperou até 36,83 °C
~17:13, com CO₂ ativo. Referência na captura 17:12:45: 36,4 °C,
Arduino pareado36,64 °C. Não recalibrar na transição. Comparações visuais
por minuto arquivadas em `docs/ensaios/referencia_recuperacao_2026-10-27.csv`
e imagens `camera_recuperacao_inicio.jpg`/`camera_recuperacao_subida.jpg`.
Pico e manutenção posteriores ainda pendentes.

## Revisão da tendência e resultado prolongado, 17:29–22:10

A revisão removeu a segunda EMA da taxa: filtra primeiro a temperatura
(com constante aproximada10s) e calcula a tendência na janela30s. Também
bloqueia pulsos com leitura >=37 °C quando a tendência é positiva.
Teste de regressão cobre inversão de resfriamento para aquecimento e o
bloqueio na meta. Isso NÃO resolveu fisicamente os picos: supervisor
interrompeu às17:42 com Arduino37,20 °C, e os dados posteriores incluíram
37,45 °C após reabilitação do controle. Essa reabilitação está no log,
sem novo ACK serial e sem reboot; origem não estabelecida.

Às22:01:32, novo enquadramento da câmera permitiu ler referência37,9 °C;
Arduino próximo de37,0 °C. A última hora naquele momento teve
36,39–37,45 °C no Arduino, média36,898 °C. Falhou tanto em estabilidade
quanto na concordância com a referência. Fonte reconstituível, hash, parâmetros
e7108 amostras arquivados em `docs/ensaios/filtro_tendencia_2026-10-27.*`.
Não usar essas medidas para mudar offset sem controlar a condição física.

## Novo recipiente e atualização parcial do visor, ~22:10

Usuário encontrou recipiente seco; adicionou25mL em outro pote, com só
um canto tocando o aquecedor. Pediu manter assim neste ensaio e comparar
sem contato depois que estabilizar em37 °C. Isso é relato físico, não medida
de temperatura da água ou umidade. Telemetria da câmara não mede RH.

Visor agora atualiza apenas as células dos caracteres alterados,7×12px,
com sobreimpressão em negrito dentro da própria célula.37.01→37.08 apaga
uma célula e desenha apenas8;36.99→37.00 altera três células. Valor idêntico
não gera desenho de temperatura. Cor/invalidade do cache forçam o campo
completo; comprimentos menores apagam caracteres antigos.
Todos os cinco testes passaram; compilação32244bytes flash e1024bytes
de RAM estática. Gravação verificada. O controle térmico não mudou nessa
atualização de visor e permanece sem aprovação física.

Novo log `coleta-visor-parcial-20261027.log`, BOOT27 (ignorar fragmentos
pré-boot), fotos `visor-parcial-camera/`. Supervisor externo `supervisao-agua25.json`
anexado ao controle já ativo às22:16, sem enviar HEAT ON; aborta aquecimento
a37,2 °C, telemetria inválida ou timeout1h. CO₂ ativo. Referência25,3 °C
às22:12:25 durante manipulação/reset; extremos reiniciados ainda a confirmar.

## Cadência e redesenho de todos os campos, 22:30–22:43

Usuário autorizou gravar a cadência mais rápida do visor. A atualização
passou do fim do ciclo de CO₂ (~2,35s medidos) para o atendimento de
entradas, a cada quatro quadros de160ms (~640ms, sujeito ao tempo de I/O).
O DS18B20 continua com conversões >=800ms. Não mudou o intervalo
intencional de espera/dosagem de CO₂ nem os parâmetros térmicos.

Após observar que os demais campos ainda apagavam inteiros, usuário pediu
atualização parcial também de CO₂, temperatura interna, ppm/min e cm³/h.
Agora todos os campos compartilham cache de caracteres e cores. Apenas
células diferentes são apagadas; repintura só de cor mantém o fundo.
Encurtamento limpa sufixos e a última célula é limitada à largura da tela.
Testes verificam os cinco campos, zero desenho com valores iguais, carry
36.99→37.00, CO₂50000→50001, INT30.0→30.1, taxa-100→-101,
perda24.0*→24.1*, cores, sufixos, cadência e modo porta. Os avanços reais
das fontes (13/7px) são decodificados no teste para validar as células.
Todos os cinco testes de controle passaram; compilação32160bytes flash,
1121bytes de RAM estática; gravação verificada ~22:41.

Etapas com água25mL interrompidas para essas alterações de visor foram
arquivadas como PARCIAIS, não aprovadas nem reprovadas pelo limite:
`agua25_pre_cadencia_2026-10-27.*` (máximo35,33 °C) e
`visor_rapido_2026-10-27.*` (máximo36,76 °C, fonte reconstituível).
Coleta atual `coleta-campos-parciais-20261027.log`, fotos
`campos-parciais-camera/`, supervisor `supervisao-campos-parciais.json`.
Retomada confirmada22:42:24, CO₂ ativo, montagem mantida25mL/canto.
Pico e patamar térmicos continuam pendentes. Referência35,0 °C e
Arduino~35,6 °C em captura atual22:34:51, ainda em transição.

Comparação adicional22:47:13 em imagem com idade0,07s: referência36,2 °C,
último DATA Arduino36,76 °C, diferença+0,56 °C; saída do aquecedor0
naquele instante, controle habilitado. Tendência ainda+0,24 °C/min.
Ainda não é patamar de calibração nem aprovação de controle. Fotos e
pares de25,3/28,01;30,0/31,39;35,0/35,58;36,2/36,76 °C em
`docs/ensaios/referencia_agua25_2026-10-27.csv` e `agua25_comparacao_*.jpg`.

## Ajuste operacional do offset, 23:09

O trecho sem novas gravações22:42–23:08 manteve Arduino no alvo:
últimos10min de controle ativo36,83–37,14 °C, média36,965 °C. Referência
repetiu36,5–36,6 °C nas imagens; pares/fotos em
`referencia_campos_parciais_2026-10-27.csv` e `camera_campos_parciais_inicio.jpg`.
Ensaio completo em `campos_parciais_antes_offset_2026-10-27.*`.

Aplicado ajuste operacional de−0,4 °C: offset+1,575→+1,175 °C. O propósito
é alinhar a leitura/controlador ao ponto de referência nesta montagem fixa.
Não é calibração intrínseca em ponto comum: uma sonda está sobre metal e
a outra livre no ar; essa diferença de montagem continua sendo uma limitação.
Ganhos, período e cortes37,1/39 °C mantidos. Verificações de software passaram,
compilação32160bytes flash/1121bytes de RAM e gravação verificada concluídas.
Foi removida do teste de relé a antiga asserção aritmética de um ponto
de calibração obsoleto; a validação do offset é física, nos pares registrados.

Validação independente iniciada em `coleta-calib-agua25-20261027.log`,
BOOT33; imagens `calib-agua25-camera/`, supervisor `supervisao-calib-agua25.json`.
Retomada automática23:10:10; CO₂ ativo. Supervisão interrompe aquecimento
a37,2 °C ou falha de dados, com timeout1h. Mesmos25mL e contato pelo canto,
sem mover sondas. Não há aprovação física ainda: verificar patamar e pico
completos dos dois sensores depois do ajuste.

## Interrupção para manutenção e mudança do pote, 23:34–23:41

Antes da manutenção, Arduino atingiu máximo37,11 °C; a referência chegou
a37,0–37,1 °C nas capturas. Pares e imagens em
`referencia_pos_offset_2026-10-27.csv` e `camera_pos_offset_*.jpg`.
O supervisor terminou porque enviamos ALL OFF para o usuário ajustar o
ventilador, não por atingir37,2 °C. Estado final preservado em
`calibracao_agua25_antes_ventilador_2026-10-27.json`.

Usuário confirmou manutenção feita e informou mudança física: pote ao lado
do aquecedor, sem ficar sobre ele; aquecimento indireto pelo piso de alumínio.
Volume restante e umidade não medidos. Não extrapolar a comparação anterior
para essa montagem. Sem nova gravação nem ajuste de offset.

Retomada HEAT ON confirmada23:40:56, BOOT33 mantido, CO₂ habilitado.
Supervisor `supervisao-pos-ventilador.json`, mesmo log calib-agua25.
Arduino35,36 °C às23:41; referência35,1 °C na imagem atual23:41:08.
ALL OFF antes da manutenção reiniciou integral; não é ensaio de recuperação
normal de porta com integral preservada. Validação térmica segue pendente.

## Patamar parcial com pote ao lado, 28/10 às00:05

Desde a primeira leitura>=37 °C:12,86min,371amostras; mínimo36,74 °C,
máximo37,11 °C, média36,921 °C, uma amostra acima37,1 °C.
Referência legível36,9 °C na captura00:04:56. Registro quantitativo em
`patamar_pote_lado_parcial_2026-10-28.json`. Não constitui aprovação para
células nem comprova recuperação após abertura normal. Esse teste físico
foi solicitado e ainda não há evento novo de porta no log. Supervisor de
porta segue ativo, sem reiniciar placa/integral; timeout~01:02 desliga HEAT.

## Patamar adicional,28/10 às00:24

Sem nova abertura registrada. Últimos20min:575amostras,36,74–37,18 °C,
média36,9576 °C;23amostras acima37,1 °C. Pico37,18 às00:13:27, sem
disparo37,2. Referência37,0 °C na imagem00:23:38, Arduino37,11 °C.
Foto `pote_lado_referencia_0023_2026-10-28.jpg` e janelas10/20/30min em
`patamar_pote_lado_0024_2026-10-28.json`. Melhora do patamar nesta montagem
não comprova recuperação após abertura; esse ensaio continua pendente.
