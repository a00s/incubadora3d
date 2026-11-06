# Teste isolado de CO₂ — preparado, não autorizado nem executado

A versão instalada é `f9f1554b`, enviada/verificada às20:41 de2026-11-06.
CO₂ e aquecimento continuam habilitados. A observação não confirmou manutenção
contínua em49.000–51.000ppm: o melhor trecho foi297,75s; os últimos10min tiveram
48.074–52.437ppm, média49.867,97ppm e64,6% das leituras na faixa.

A comparação entre doses e subidas fica ambígua quando várias respostas se
sobrepõem e parte do gás apenas repõe perdas. Um ajuste aproximado do log teve
erro de validação de cerca de1.206ppm, maior que a meia faixa de1.000ppm.
Esses dados não sustentam declarar o controle estável nem identificar uma vazão
exata a partir de uma pequena subida líquida.

## Protocolo proposto

1. Usar uma captura de quatro minutos, sem alterar estados salvos na EEPROM nem
   o aquecimento. O firmware de captura adia o automático até240s após boot;
   depois desse prazo o automático pode retomar pelas condições existentes.
2. Registrar os primeiros120s sem abrir a válvula, para observar a evolução
   sem doses novas. O gás de doses anteriores ainda pode estar misturando;
   não assumir que toda queda mede apenas vazamento externo.
3. Perto de120s, aplicar **um único comando `CO2 PRIME` de20ms**, somente com
   leitura atual válida, abaixo de49.000ppm, controles habilitados e sem trava.
   Se essas condições não forem atendidas, não aplicar nem estender a pausa
   automaticamente. Não repetir o comando por ausência de ACK.
4. Registrar por mais120s sem outro comando manual. Medir atraso até a resposta,
   vale/pico, evolução sem injeção e duração da resposta. Uma única medição não
   certifica qualquer cilindro ou substitui validação posterior.
5. Ao fim, revisar os dados e restaurar a versão normal antes de encerrar o
   teste. Não enviar `CO2 OFF`, `HEAT OFF`, `ALL OFF` nem desbloqueio. Um reinício
   durante a captura conserva os estados EEPROM; o período de240s recomeça.

O pedido de autorização decorre da instrução anterior do usuário:
**“nada de pausa de observação”**. Este teste seria uma exceção temporária e
explícita. Não foi realizado enquanto a resposta está pendente.

## Preparação verificável

`scripts/prepare_co2_isolated_capture.py --compile` prepara uma cópia separada
em `.arduino-build/isolated_capture_sketch` e compila; não envia firmware nem
comandos. A diferença em relação ao sketch normal é somente:

- espera inicial CO₂ de120.000 para240.000ms;
- argumento padrão do comando manual de5 para20ms; botões, mínimo automático,
  limites e estados gravados permanecem no código normal.

A compilação preparada passou:32.222bytes Flash e1.195bytes RAM estática.
O manifesto em `.arduino-build/isolated_capture_prepared.json` e sua cópia
versionada registram hashes. Os binários de captura ficam separados do build
normal. Não usar o journal de upload normal com hashes da fonte errada: um
upload autorizado da captura deve registrar o sketch temporário e seu HEX.

O controlador e o logger de produção não foram alterados por esta preparação.
