## Porta monolítica com vedação em U — v48

Porta rígida em uma peça: painel interno integrado, sem painel removível, linguetas de união, alojamento cego ou parafusos extras. Canal perimetral em U rebaixado na face interna recebe uma borda contínua integrada ao corpo. Junta `junta_U_porta_TPU.stl` com pé alargado retido no canal e dois lábios de 0,6 mm, um de cada lado da borda. A junta externa `junta_porta.stl` do corpo foi preservada como segunda linha de vedação.

Canal: profundidade 2,9 mm; boca 2,2 mm; centro a 3,4 mm do contorno nominal. Borda rígida: largura 1 mm, projeção frontal 2,5 mm e chanfro de entrada de 0,3 mm. Folga rígida lateral nominal: 0,6 mm por lado na boca. TPU exibido em forma livre; deformação, retenção e estanqueidade precisam de ensaio físico.

Câmara rígida preservada: largura 112 × altura 132 × profundidade 111 mm, cantos R6. Revestimento inox 304: dimensões externas 111 × 131 × 110 mm, R5,5 e espessura 0,05 mm. Medidas internas do revestimento: 110,9 × 130,9 × 109,95 mm. O molde é referência de conformação, sem planificação nem compensação de dobras. Alterar a espessura exige revisar o molde.

Orientação da porta e planejamento de suportes adiados por solicitação do usuário. Orientações no projeto 3MF são apenas iniciais; não constituem validação para impressão. Arquivos atuais em `output/v48/`.

Validação v48: 57 pares rígidos com envelopes sobrepostos conferidos, sem colisões. Movimento da porta em 0°, 0,5°, 1°, 2°, 5°, 15°, 30°, 60°, 90° e 110°; entrada do inox livre a 110°. STLs dimensionados para K1C com margem de 5 mm. Projeto 3MF com 35 bandejas, estrutura, escala e índices conferidos; leitura nativa no Creality Print 7.2.1 via CLI --info com saída 0. Sem fatiamento ou G-code. Amostras de 35 mm: `amostra_U_porta_rigida.stl`, `amostra_U_porta_TPU.stl` e `amostra_U_borda_corpo.stl`; permitem ensaio manual de encaixe, sem comprovar estanqueidade nos cantos.

Visualizador v48 conferido no Chromium: junta TPU do U presente, painel separado ausente e sem erros JavaScript. Corte esquemático em `corte_vedacao_U.svg`. Apenas corpo e porta mudaram entre os STLs preexistentes; a junta do U e três amostras foram acrescentadas.
