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

**Estabilidade física da segunda etapa ainda em acompanhamento.**
O trecho inicial truncado da nova coleta é descartado; usar as amostras
contínuas após `BOOT_COUNT,6` e verificar se não houve outro reinício.

## Coleta e limites

Logs completos e capturas de diagnóstico ficam em
`/tmp/incubadora-telemetria/`; esse armazenamento é temporário.
Imagens pareadas e metadados: `pos-ajuste-camera/observations.jsonl`.
Log posterior ao ajuste: `coleta-pos-ajuste-20261027.log`.
Log da segunda etapa: `coleta-periodo20-20261027.log`; imagens e metadados
em `periodo20-camera/`.

A análise de objetos do RoomCam foi desligada, mantendo o vídeo e as
capturas. O coletor serial passou a esperar dados com `select`, sem
ocupar uma CPU inteira. Testes com pseudoporta verificaram espera ociosa,
preservação do texto e extração de quadros binários MH-Z16.

As verificações de software não comprovam desempenho térmico, precisão
absoluta dos termômetros, temperatura do líquido ou uniformidade espacial.
Nenhuma peça CAD ou configuração do projeto de impressão foi alterada.
