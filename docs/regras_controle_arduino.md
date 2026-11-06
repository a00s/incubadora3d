# Regras atualmente presentes no firmware

Auditoria de 2026-11-06. Esta lista descreve o código, não valida a regulação
física. Parte destas regras foi acrescentada durante as revisões; não deve ser
confundida com o funcionamento original solicitado pelo usuário.

## Alterações explicitamente pedidas nesta revisão

- Restaurar os últimos estados ligado/desligado de CO₂ e aquecimento da EEPROM.
- Não sobrescrever esses estados ao iniciar o Arduino.
- Remover desligamento e trava por diferença de ±15.000 ppm entre leituras.
- Manter as demais regras sem alterações nesta revisão.

O número 15.000 permanece somente para registrar `EVENT,co2_fast_change` no log.
Esse registro não desliga controles, não grava trava e não altera EEPROM.
Eventos de bloqueio registrados por versões anteriores continuam no histórico.

## Persistência e reinício

| Comportamento | Implementação atual |
|---|---|
| Estado ligado/desligado | `saveControlState`, `setCo2Enabled`, `setHeaterEnabled`, em `temperatura.ino`. Salvo no byte 29 da EEPROM. |
| Retorno de energia | Lê os estados salvos; não há mais a regra `CO2_EXPERIMENTAL_START_DISABLED`. |
| Porta pausada | Byte 29 também guarda pausa e os estados a retomar. Um reinício durante a pausa conserva essa pausa. |
| Trava de concentração | Byte 28 conserva a trava; ela tem prioridade sobre CO₂ ligado. Reiniciar não a limpa. |
| Falha térmica | Byte 30 guarda o código da falha; o desligamento dos controles também salva seus estados. |
| Limpar trava | Atualmente mantém o automático desligado; é necessário escolher novamente o estado ligado. Essa regra não foi modificada nesta revisão. |
| Aprendizado | Histórico de doses e integral térmica ficam na RAM, não na EEPROM. As metas 50.000 ppm e 37 °C ficam no programa. |

A regra anterior já havia sobrescrito o estado do CO₂ para OFF. A correção não
adivinha um estado substituto: preserva o que está salvo, e a próxima escolha
ligado/desligado feita pelo usuário é gravada normalmente.

## Dosagem automática de CO₂

Fonte: `firmware/incubadora/co2_dosing.h` e condições de admissão em
`temperatura.ino`. Estes são os valores ativos, inclusive os que não foram
definidos explicitamente pelo usuário.

| Regra | Efeito |
|---|---|
| Meta 50.000 ppm | Entra no erro usado para calcular a dose. |
| Faixa 49.000–51.000 ppm | Referência visual e de recuperação. Recuperação usa déficit até50.000 ppm; reposição prevista pode usar a margem até51.000. Sem nova dose a partir de51.000 ppm, sem necessariamente desligar a habilitação. |
| Espera inicial 120 s | Não injeta durante esse tempo após reinício, mesmo habilitado. Foi acrescentada nas revisões; o primeiro código importado esperava10s. |
| Histórico de 16 leituras e janela ≥30 s | Outra condição para liberar doses. É preenchido em paralelo ao aquecimento inicial; uma leitura inválida reinicia esse histórico. |
| Intervalo mínimo 20 s | Entre o fechamento da válvula e nova abertura automática. Pedido pelo usuário. |
| Duas quedas dentro de 20 s | Podem liberar a dose se as outras condições permitirem. Pedido pelo usuário. |
| Platô | Duas variações dentro de ±2 ppm/s são tratadas como estabilidade. Essa tolerância numérica foi introduzida nas revisões. |
| Até 5 escadas | Ganho ponderado: soma das subidas dividida pela soma das aberturas associadas à resposta; usa imediatamente1–5 referências disponíveis. Não atribui toda resposta à última abertura se ela ainda está em trânsito. |
| Subida mínima 200 ppm para aprender | Variações menores não atualizam o ganho. Não impede continuar a calibração. Esse filtro foi introduzido nas revisões. |
| Calibração 20/40/60/80… ms | Enquanto não existe ganho útil. Pedido pelo usuário. |
| Aumento máximo 20 ms | Aplica-se também às doses calculadas após aprender; reduções podem ser maiores. Pedido pelo usuário. |
| Abertura mínima 5 ms e máxima 100 ms | Teto de 100 ms pedido explicitamente pelo usuário. Vale para calibração e doses aprendidas. Não é declaração de limite físico da válvula. O primeiro código importado usava 1–60 ms; o teto de 1.000 ms das revisões foi removido. |
| Compensação de perda | A antiga perda estimada×tempo de resposta foi removida. Reposição experimental: ritmo de ms comandados nas últimas5 aberturas, convertido ao equivalente de20s pelo ganho medido, limitado a1000ppm; somado ao déficit e descontado o gás previsto em trânsito. |
| Estimativa da perda | O estimador filtrado80/20 foi removido do modelo de dose. A estatística independente de perdas do visor permanece. Reposição usa o ritmo dos comandos, que não é uma medição física isolada de perda. |
| Religar CO₂ | Preserva o histórico de ganho e os tempos de resposta já medidos. Limpa somente atribuição inacabada e tendência. Uma leitura inválida faz o mesmo; não transforma ON/OFF em reset de processador. |
| Leitura inválida | Impede injeção e limpa tendência/atribuição inacabada, preservando ganhos úteis. A habilitação pode continuar ligada. |
| Botões em processamento | Sequência do botão de CO₂ ou pressão pendente no botão térmico suspendem a dosagem automática. |

O ganho agora usa somente a subida observada; a antiga soma de perda ao ganho foi
removida. Não existem mais o orçamento acumulado de 66 ms, ganho presumido de 800 ppm/ms,
alerta/desligamento por falta de subida ou bloqueio de variação ±15.000 ppm.

## Contagem de respostas atrasadas

Fila de até5 comandos. A primeira escada útil mede chegada (vale) e fim (pico)
com chegada a partir do comando mais antigo ainda sem resposta e duração até o pico a partir do último comando que contribuiu para a escada. Assim, não inclui os intervalos entre as doses na duração da resposta. Esses tempos ficam retidos
até reset completo; dentro dessa janela, a quantidade prevista restante é
descontada do déficit. Não acrescenta um temporizador fixo de observação: se o
déficit superar a quantidade pendente, pode dosar após os20s habituais.

Limitações verificadas: mais de5 comandos pendentes podem sobrescrever a
atribuição antiga; o primeiro tempo medido não acompanha automaticamente nova
geometria de mistura. Calibração cega20/40/60… antes de qualquer resposta ainda
pode exceder a meta com vazão alta/atraso grande. A suíte de stress conserva
essas falhas; não é certificação de estabilidade em qualquer cilindro.

## Condições que ainda desligam ou impedem os controles

| Condição | Resultado |
|---|---|
| Leitura de CO₂ ≥60.000 ppm | Desliga CO₂ e grava trava na EEPROM. Mantida nesta revisão. |
| Mudança grande abaixo de 60.000 ppm | Apenas registra variação; não bloqueia por esse motivo. |
| Temperatura ≥39 °C | Desliga CO₂ e aquecimento e grava a falha. |
| Falha do sensor térmico por 60 s | Desliga CO₂ e aquecimento e grava a falha. O aquecedor é cortado antes desse prazo enquanto a leitura estiver inválida. |
| Porta marcada aberta pelo botão | Pausa ambos e impede doses manuais; fechar restaura os estados anteriores se as outras condições permitirem. |
| Pedido explícito OFF/ALL OFF | Salva o estado desligado na EEPROM. |

Um valor baixo após retorno do contador não comprova concentração baixa. A
visualização reconstruída com≈ não é usada pelo controle e não limpa travas.

## Temperatura, botões e apresentação

- A leitura térmica recebe offset +1,175 °C, aplicado também ao controle.
- O aquecimento usa PID, previsão térmica de 1,5 min, corte normal 37,1 °C,
  janela 20 s, até 17 s ligado e mínimo 3 s desligado. Esses parâmetros constam das
  revisões térmicas anteriores; não foram alterados nesta correção de persistência.
- Ventoinha interna liga a 31 °C e desliga abaixo de 30 °C.
- Toque longo de 2 s no botão térmico alterna a pausa de porta.
- Três/quatro/cinco toques no botão de CO₂ comandam pulsos manuais de 5/10/20 ms.
  Esses comandos não seguem o intervalo automático de 20 s e não ligam o automático.
- Com trava ativa, três toques no botão térmico a limpam, mantendo CO₂ OFF.
- O painel web não envia comandos de atuação. Valores após retorno do contador
  são estimativas visuais identificadas, preservando leitura bruta e validade.

## Declarações antigas sem efeito ativo

`CO2_MAX_RISING_RATE_PPM_PER_MIN`, `CO2_STABLE_TIME_MS`,
`CO2_RESPONSE_LAG_DEFAULT_MS`, `CO2_RESPONSE_LAG_MAX_MS` e
`CO2_DOSE_OBSERVATION_MS` ainda aparecem como definições antigas, mas não são
consultadas pelo caminho atual de dosagem. A presença de um número nessas
declarações não significa que exista essa espera ativa.

## Referência histórica

O commit `7c29d42` contém o primeiro `temperatura.ino` importado, com restauração
dos estados da EEPROM e limite automático1–60ms. Ele também usa a configuração
antiga de sensores. Restaurar o arquivo inteiro sem comparar ligações e controle
térmico não equivale a recuperar somente a lógica original de CO₂.
