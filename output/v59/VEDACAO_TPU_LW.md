# Vedação removível da porta e dos cabos — eSUN TPU-LW

**Não retirar nem mexer na junta que já está encaixada na caixa da incubadora.**
O PC está quebradiço. As fotos de montagem confirmam duas juntas separadas;
Todas as peças flexíveis do projeto usam agora eSUN TPU-LW, incluindo a bucha
do sensor CO₂, as duas juntas, as rolhas dos fios e suas amostras. Os encaixes rígidos são preservados. A bucha CO₂ recebe um bulbo inferior oco
conforme as medidas do sensor; o fluxo compensa a expansão nominal do material.
A junta instalada na caixa não precisa ser retirada.
Porta, corpo, dobradiças, fecho, gavetas e bucha redonda do sensor são preservados.

## Junta da porta

Mantém a retenção no canal em V existente da porta, com pé de entrada gradual. Uma ligação recuada sustenta um
tubo oco alongado, com cavidade interna mais alta e paredes finas para
dobrar sob pressão. A vedação
encosta na face frontal remanescente e robusta do corpo em Y=0, entre o canal
da junta da caixa e a abertura. Não usa a pequena borda fina quebrada como
apoio ou batente; também não precisa extrair a junta da caixa.

O perfil foi redesenhado como uma base de encaixe, pescoço e cabeça oca
volumosa, conforme a fita de vedação fotografada pelo usuário. O bulbo chega
a **4,70 mm de largura**, com cavidade de **3,60 mm** e peles laterais de cerca
de 0,55 mm. A seção usa transições graduais e teto inclinado para imprimir
sem suportes; o formato aproxima um bulbo arredondado, com teto imprimível.

O bulbo aprovado é mantido até X90. Os últimos 30 mm das travessas fazem a
transição para uma cabeça menor no lado das dobradiças (X110–120). A ponta
livre junto à dobradiça passa de **4,50 para 2,00 mm**. A altura total passa
para **6,25 mm** nessa lateral, mantendo **9,95 mm** e ponta Y=5,70 no fecho.
A cabeça da dobradiça também fica mais estreita: cerca de **2,68 mm**, com
cavidade de **1,58 mm** e peles nominais de 0,55 mm. A base de encaixe não muda.

A redução localizada libera o volume que encontra primeiro a caixa durante
o fechamento inclinado. A seção CAD não prevê força de fechamento: testar
a amostra da dobradiça antes do anel. A junta da caixa permanece instalada.

Um respiro **Ø0,8 mm** atravessa somente a parede externa do bulbo, na lateral
do fecho, altura Z70. Liga a cavidade à atmosfera externa para aliviar o ar
preso durante a compressão. Não perfura a parede interna que separa a cavidade
da câmara. Não tapar o respiro com adesivo; testar passagem de ar e estanqueidade.

A largura máxima do pé passa de 0,59 para **0,94 mm** (+0,35 mm). O canal
rígido tem 1,65 mm no fundo, mas entrada estreita e pouca profundidade:
aumentar 1 mm inteiro neste perfil comprometeria a rampa imprimível sem suporte.
Esta versão testa maior retenção preservando a rampa e a porta existente.
A maciez e a retenção finais precisam ser conferidas na amostra física.

Imprimir deitada, com a ligação traseira plana na mesa e o bulbo para cima
(+Y do CAD), sem suportes. A porta rígida continua com a frente externa plana
na mesa; esta alteração não exige reimprimi-la. Começar pela amostra recortada
do mesmo perfil da junta. Somente o pé flexível recebe uma rampa mais suave para impressão; o canal
rígido da porta permanece intacto. Conferir a retenção na amostra antes do anel.

## Anel do sensor CO₂

Medidas do sensor fornecidas pelo usuário: tubo **Ø15,57 mm** e anel junto à
cabeça **Ø16,60 mm × 3,18 mm de altura**. O apoio superior que vedou bem fica
preservado a partir de Z local 5,32 mm. A flange, a manga Ø19,8 mm, o furo rígido
Ø20,4 mm e os dois lábios internos/externos mantêm a geometria existente.

Um bulbo anular oco adicional pressiona o cilindro inferior, com abertura livre
**Ø15,00 mm** na peça principal e compressão radial nominal de **0,285 mm**.
A pele interna nominal é de 0,55 mm; a cavidade permite ceder radialmente.
As raízes dos lábios são mantidas e cruzam parte da cavidade. A bucha é uma
única peça, sem acrescentar componentes nem alterar o corpo rígido.

| Bandeja separada | Lábios internos | Bulbo inferior livre |
| --- | --- | --- |
| 7 — bucha principal | Ø15,20 mm | Ø15,00 mm |
| 8 — amostra `_15.3` | Ø15,30 mm | Ø15,10 mm |
| 9 — amostra `_15.5` | Ø15,50 mm | Ø15,30 mm |

Os sufixos dos arquivos continuam indicando o diâmetro dos lábios, não o novo
bulbo. Começar pela bucha principal da bandeja 7; as amostras oferecem aperto
menor caso a impressão fique justa demais. Imprimir com a face externa do colar
na mesa, sem suportes, mantendo 270 °C / fluxo experimental 55%. Retenção,
força de inserção e estanqueidade precisam de ensaio físico.

[Corte radial extraído do STEP](corte_bucha_CO2_TPU_LW.svg).

## Cabos

Rolhas bipartidas para os mesmos furos Ø12 × 14 mm e fios existentes:
aquecedor 2 × Ø1,42; sensor lateral 3 × Ø1,40 mm. Corpo livre Ø12,24 mm e canais
Ø1,26 / Ø1,24 mm, com entradas chanfradas. Contato contínuo em lugar dos lábios
isolados anteriores. A interferência deve comprimir a espuma contra o furo,
os fios e entre as metades. A flange Ø16 × 1,5 mm permanece somente externa.
Não trocar metades entre as duas rolhas; não puxar os conectores através delas.

## Arquivo para imprimir

Abrir **`vedacoes_eSUN_TPU_LW.3mf`**, com doze bandejas:

| Bandeja | Peça |
| --- | --- |
| 1 | Amostra do lado da dobradiça da junta da porta |
| 2 | Junta inteira da porta |
| 3 / 4 | Aquecedor, metades A / B |
| 5 / 6 | Sensor lateral, metades A / B |
| 7 | Bucha CO₂: bulbo Ø15,0 mm + lábios Ø15,2 mm |
| 8 / 9 | Amostras CO₂: bulbos Ø15,1 / Ø15,3 mm |
| 10 | Junta da caixa, para reposição futura |
| 11 / 12 | Amostras da junta da caixa, lábios de 0,6 / 0,8 mm |

O perfil mantém material contínuo entre base, pé e bulbo; a amostra inclui
a cabeça inteira reduzida do lado da dobradiça, sem o respiro que fica no fecho.
As alturas são 9,95 / 6,25 mm.
O fatiamento das doze bandejas passa sem avisos de regiões suspensas e sem
suportes, com a detecção do fatiador ativa. Imprimir primeiro a amostra para
conferir encaixe, compressão e calibração do material.

Cada bandeja contém uma peça. Os STL/STEP `*_metade_A` e `*_metade_B` já têm
a flange na mesa. No projeto completo, as peças atualizadas ficam nas bandejas
originais: junta da porta 16, amostra 21, rolhas pareadas 11/12. Os pares do
projeto completo são referências: não imprimir as duas metades simultaneamente.
A junta da caixa e suas amostras mantêm a geometria e agora usam o mesmo perfil TPU-LW.

O Creality Print 7.2.1 limita o projeto a 36 bandejas e alguns ajustes, como
velocidade da primeira camada, são globais. Por isso, o arquivo separado tem o
processo completo para TPU-LW; o projeto completo mantém as configurações gerais
salvas e atribui o perfil TPU-LW a todas as dez peças flexíveis. O perfil antigo
TPU 85A fica salvo, mas sem nenhuma peça atribuída.

## Perfil revisado após teste a 230 °C / 70%

- Bico 270 °C, mesa 50 °C, camada 0,2 mm, velocidades de extrusão 25 mm/s.
- Retração normal, de camada e de troca: 0; wipe e Z-hop desativados.
- Ventilador 100% após a primeira camada; ventilador auxiliar desligado;
  sem redução automática de velocidade por resfriamento; sem suportes.
- Três paredes e preenchimento 100% no material da junta. A cavidade desenhada
  continua vazia porque está no CAD, independentemente do preenchimento.
- Fluxo **0,55 a 270 °C**, estimativa entre os pares 256 °C/0,60 e
  280 °C/0,50 do gráfico enviado. A página atual eSUN recomenda 210–270 °C;
  este teste usa o limite recomendado, mantendo retração desativada.
  O fluxo de 55% precisa ser calibrado na amostra; não é um par certificado.

A temperatura e a velocidade estão nas faixas do
[TDS eSUN](https://www.esun3d.com/media/esun/catalog/certification/product/TPU-LW/TPU-LW_TDS_V1_.pdf).
A [página oficial](https://www.esun3d.com/etpu-lw-product) exige ajustar o fluxo
à expansão, desligar retração e imprimir uma peça por vez. Secar a 55 °C por
mais de quatro horas; usar extrusor direto, bobina externa seca e tubo curto.
Não assumir que o fluxo do TPU convencional serve para o material espumado.

Medir a amostra e conferir paredes contínuas, sem vazios. Se a extrusão medida
ficar maior que a nominal, reduzir o fluxo proporcionalmente; se faltar material,
aumentar. Manter temperatura e velocidade fixas nesse ajuste. Ao mudar temperatura
para alterar maciez, recalibrar fluxo e encaixe. Limpar fios da impressão sem
cortar a pele da junta.

## Montagem e ensaio

Retirar somente a junta da porta. Assentar o novo pé no canal da porta por todo
o contorno, sem torcer o anel. Fechar lentamente, com a lateral menor junto à
dobradiça, e apertar o fecho aos poucos. Parar se exigir força excessiva no PC.
Conferir contato contínuo com uma tira de papel em diferentes pontos.

Comparar a queda de CO₂ nas mesmas condições de concentração, temperatura,
umidade e tempo, verificando porta e cabos separadamente. A ficha eSUN não
especifica permeabilidade ao CO₂ nem garante estanqueidade da espuma impressa.
Redução de vazamento, força, recuperação elástica, fluxo e compressão finais
permanecem pendentes de ensaio físico.

## Arquivos corrigidos: small_perimeter_speed

Se o Creality Print mostrar `DynamicConfig::opt_float()` para
`small_perimeter_speed`, fechar o projeto antigo e reabrir o 3MF corrigido.
A sobrescrita individual de 100% foi removida; no arquivo separado, a velocidade
passa a ser herdada do valor global absoluto de 25 mm/s. Essa correção continua nesta revisão do tubo. Não salvar o projeto antigo sobre o arquivo corrigido.
