# Rampas dentro das paredes — v58

A carcaça imprime com a traseira Y125 na mesa, crescendo na direção −Y.
Os apoios das dobradiças e da lingueta entram parcialmente nas cavidades
fechadas da camada de isolamento. Na v57, a união dos apoios criava tetos
retos dentro dessas cavidades, apesar das rampas externas existentes.

Foram acrescentadas rampas internas a 45° em três locais:

- Duas dobradiças: na cavidade X122–128, o apoio cresce do material existente
  em X128/Y10 até X124/Y6. Altura de cada rampa: 8 mm.
- Base da lingueta: na cavidade X−8–−2, o apoio cresce de X−8/Y13,75
  até X−4,25/Y10. A rampa atravessa os 20 mm de altura do apoio.

As rampas ficam na camada de isolamento; os furos das dobradiças, a rosca,
a guia do fecho e os perfis da porta continuam nas mesmas posições.
Os furos não foram alterados para formato triangular. A correção refere-se
às cavidades dentro das paredes, atrás dos apoios.

A verificação das faces da carcaça final, depois de todas as uniões,
confirmou rampas a 45° nas três regiões. Nas dobradiças não restou teto reto;
na lingueta permanecem apenas trechos da ponte nominal de 0,4 mm do isolamento,
com área plana total inferior a 1 mm². Não há o antigo teto largo do apoio.

A amostra `amostra_dobradica_base_M4x20.stl` agora é um recorte da parede
oca real da carcaça, incluindo as rampas interna e externa. Imprima com
a orientação fornecida para conferir esse detalhe antes da carcaça inteira.

Relatórios: `internal_mount_roof_report.json` (faces finais),
`mount_wall_before_after_report.json` (reprodução local antes/depois)
e `clash_report.json` (montagem). Refatie a carcaça e confira a prévia de
camadas com seus parâmetros de suporte: não há G-code nem ensaio físico
nesta revisão. Somente o corpo e a amostra da dobradiça mudaram; a porta,
as gavetas e os outros 34 STL são idênticos aos da v57.
