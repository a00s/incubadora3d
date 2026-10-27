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
