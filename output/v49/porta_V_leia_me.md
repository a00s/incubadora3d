## Ressalto inteiro em V com fundo plano — v49

A alteração se aplica a todo o ressalto interno da porta, não só a um canal estreito. A peça rígida é única: base larga e ponta menor, com laterais inclinadas e cantos contínuos. O corpo recebe um assento perimetral inclinado, mais largo na boca, integrado ao quadro frontal. O fecho mantém a carga axial; a cunha comprime os lábios TPU lateralmente. Não há validação de autotravamento nem simulação de contato/deformação.

Inclinação do ressalto: avanço radial de 0,5 mm por mm axial, 26,565° em relação ao eixo de fechamento. Base do ressalto em Y−4,6 com inset 2,65 mm; ponta em Y3 com inset 6,45 mm. Dimensões X/Z: base 114,7 × 134,7 mm; ponta 107,1 × 127,1 mm. Cantos seguem o centro dos raios da câmara e do inox, em X/Z10. Assento do corpo: boca em Y−3,7 e inset 2,47375 mm, convergindo até inset 4 em Y0. Espessura radial nominal 1 mm. A abertura no plano Y0 permanece 112 × 132 mm. Geometria de ponta/ângulo da porta e assento são diferentes para manter folga rígida e espaço de deformação do TPU.

`junta_V_porta_TPU.stl` envolve o ressalto inclinado; pé retido numa ranhura com seção alargada, dois lábios anulares axiais de 0,6 mm. A junta do corpo continua com dois lábios, mas o lábio originalmente voltado para dentro foi redirecionado para fora, para liberar o assento em V. As peças TPU são exibidas em forma livre; interseções intencionais com as superfícies de vedação não representam colisões rígidas. Não se presume estanqueidade, esforço de aperto ou vida útil sem ensaio físico.

Inox comprado: 0,3 mm. Caixa metálica externa preservada em largura 111 × altura 131 × profundidade 110 mm, R5,5. Espaço interno e molde: 110,4 × 130,4 × 109,7 mm, R5,2. Suporte das bandejas reduzido para largura 109,8 mm, com folga lateral de 0,3 mm por lado; pés elevados para a face interna do inox em Z4,8. O molde antigo de 0,05 mm não deve ser usado para esta chapa. A planificação de corte e as compensações das dobras não estão incluídas.

Amostras de 35 mm: `amostra_V_porta_rigida.stl`, `amostra_V_porta_TPU.stl` e `amostra_V_assento_corpo.stl`. Testam encaixe e compressão numa lateral; extremos abertos e ausência de cantos impedem comprovação de estanqueidade da caixa completa.

Orientação de impressão da porta e suportes permanecem adiados por solicitação do usuário. O projeto 3MF traz orientações iniciais, sem fatiamento nem G-code. Arquivos atuais em `output/v49/`; corte da lateral inclinada em `corte_vedacao_V.svg`.

Referência do sensor de temperatura/umidade deslocada 0,3 mm para baixo (Z119,7–134,7), liberando o canto superior do inox de 0,3 mm. A fixação real do módulo permanece dependente das dimensões físicas.

Validação v49: 57 pares rígidos com envelopes sobrepostos, sem colisões; porta e inox conferidos em 20 posições entre 0° e 110°, incluindo 7°, 10°, 12°, 18° e 20°. Entrada do inox livre a 110°. Todos os STL cabem na K1C com margem de 5 mm. Projeto 3MF com 35 bandejas, escala e índices conferidos; leitura nativa no Creality Print 7.2.1 CLI --info com saída 0 e 35 malhas manifold. Visualizador conferido no Chromium, sem erros JavaScript, WebGL com conteúdo e controles de fecho/porta/bandejas funcionando. Sem fatiamento ou G-code; retenção e estanqueidade exigem ensaio físico.
