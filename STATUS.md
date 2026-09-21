# Estado atual — v0.30

- Arquivos atuais: `output/v30/`; histórico de revisões no README.
- Uma lingueta central em Z70, com manípulo/haste e porca impressos.
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
- Rosca do fecho Ø8/passo2; montagem por canal lateral e aperto pela frente.

## Validação geométrica

Auditoria estática de peças rígidas, incluindo carcaça, continuidade das
passagens e núcleo maciço das roscas. Envelopes conservadores representam
as peças roscadas contra os demais componentes; compressão TPU excluída.
Todos os testes de movimento e caminhos de montagem foram adiados a pedido
do usuário. Executar futuramente uma única rodada com:
`python cad/model.py --check-movements`.
Relatórios: `output/v30/build.log`, `clash_report.json` e
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

Manípulo: haste lisa por 24 mm e rosca apenas nos 7 mm finais junto à porca.
