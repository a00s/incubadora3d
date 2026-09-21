# Estado atual — v0.32

- Arquivos atuais: `output/v32/`; histórico de revisões no README.
- Uma lingueta central em Z70, com haste Ø8 e rosca fêmea integrada à base.
- Puxador em X17, aproximado 12 mm do fecho em relação à v27.
- Dois pés integrados 16 × 16 mm somente sob a lateral CO₂/eletrônica,
  base em Z-10, coplanar ao fundo da câmara.
- Tampa de manutenção com quatro pinos (dois superiores e dois inferiores).
- Bucha do sensor com aba Ø16 e passagem Y90/Z127,5.
- Gavetas com profundidade 72 mm e folga de 26 mm até a chapa de referência.
- Alimentação com caixa encaixada e furo Ø8; fios do aquecedor 2 × Ø1,68 mm,
  canais TPU Ø1,60 mm. Sensor: 3 fios Ø1,36 mm, canais TPU Ø1,30 mm.
- `cad/build_viewer.py` gera os dois HTML a partir da mesma malha atual.

- Quatro cantos fechados apenas na frente com tampões de 3 mm;
  cavidades de ar atrás e canal da junta TPU preservados.
- Passagem entre câmaras Ø4, sem tubo; diâmetro inicial de ensaio.
- Pinos de dobradiça com cabeça e ponta roscada Ø4/passo1; porcas impressas.
- Rosca do fecho Ø8/passo2 integrada ao apoio, sem porca nem abertura lateral.
- Tampa CO₂: três parafusos impressos Ø4/passo1 e roscas integradas na base,
  sem porcas ou canais laterais; arruelas mantidas.

## Validação geométrica

Auditoria estática de peças rígidas, incluindo carcaça, continuidade das
passagens e núcleo maciço das roscas. Envelopes conservadores representam
as peças roscadas contra os demais componentes; compressão TPU excluída.
Todos os testes de movimento e caminhos de montagem foram adiados a pedido
do usuário. Executar futuramente uma única rodada com:
`python cad/model.py --check-movements`.
Relatórios: `output/v32/build.log`, `clash_report.json` e
`compatibilidade_k1c.json`. Verificação estática não garante movimento.

## Pendências físicas e de projeto

- Ensaio de vedação com fecho único, especialmente topo e base da porta.
- Testar retenção/resistência de roscas, pinos, encaixes e estabilidade lateral.
- Filamentos e dureza TPU; compressão e estanqueidade das vedações.
- Conector de alimentação real, potência do aquecedor, chapa e sua fixação.
- Altura/fios da PCB e suporte definitivo do sensor de temperatura.
- Escape/alívio, pressão, limpeza, condensação e desempenho térmico/CO₂.
- Validar passagem Ø4 com vazão real; o furo não garante bloqueio de umidade.
- Fatiamento, orientação e suportes antes de imprimir.

Sem validação operacional ou simulação térmica/de escoamento.

Visualizador: corte horizontal ajustável entre −10 e 150 mm, com fechamento
das superfícies seccionadas e cavidades internas preservadas.

Manípulo: haste lisa por 24 mm e rosca apenas nos 7 mm finais junto à rosca integrada.

Haste lisa Ø8 mm, com folga radial de 0,35 mm no apoio e na lingueta.

Traseira do corpo e da tampa lateral niveladas em Y125, sem ressalto.
Guias e pinos inferiores recuados; envelope do corpo 190 × 141 × 160 mm.
Profundidade interna nominal da eletrônica: 22,5 mm.

Lingueta ampliada com aba para os dedos, três relevos de pega e chanfro
na face de contato. Sem testes de movimento nesta revisão.
