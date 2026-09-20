# Estado atual — v0.26

- Corpo único com misturador e eletrônica na mesma faixa lateral; traseira da caixa em Y125.
- Tampa eletrônica embutida com quatro pinos de encaixe, sem parafusos; RJ45 lateral acima da placa.
- Porta e paredes da câmara aquecida com cavidades de ar.
- Duas passagens com mangas sólidas: 3 fios na lateral superior junto da eletrônica (Z125) e 2 fios na traseira.
- Sensor e aquecedor: buchas TPU únicas; passar as pontas dos fios antes de conectar.
- Sensor de temperatura/umidade e aquecedor 90 × 33 mm como referências de posição.
- Bucha TPU do sensor CO₂ e recorte keystone direto na parede, com amostras para teste.
- Arquivos atuais: output/v26/; dimensões verificadas em compatibilidade_k1c.json.

Pendentes: teste de compressão das vedações dos fios, rosca da tomada de alimentação, potência do aquecedor,
espessura e fixação da chapa, altura e fios da PCB, suporte do sensor de temperatura,
testes de encaixe e vedação, filamentos, escape/alívio e pressão, fatiamento/suportes,
limpeza e desempenho térmico. Sem validação operacional.

Fios do aquecedor confirmados: 2 × Ø1,68 mm; canais TPU Ø1,60 mm para teste.

Sensor: 3 fios Ø1,36 mm, canais TPU Ø1,30 mm; conexão feita internamente.

Gavetas 72 mm de profundidade, trilhos encurtados e batentes traseiros; folga até a chapa de referência: 26 mm.

Entrada CO₂ inferior recolhida, voltada para a traseira; acesso à mangueira livre.
Dois furos traseiros genéricos removidos. Escape/alívio ainda pendente.
Tampo estreito de encaixe cobre apenas o percurso dos fios; cabeça do CO₂ exposta.
Entradas laterais para as três porcas M4 da tampa, acessíveis pela lateral.
Compartimento separado de alimentação 12 V alinhado com a saída superior dos fios do aquecedor.
Caixinha arredondada 36 × 21 × 30 mm, com dois pinos de encaixe direto em furos cegos da carcaça. Furo Ø8 à direita olhando por trás (-X). Uma única bucha TPU do aquecedor, sem prensa, suporte, trilhos ou parafusos. Retenção e vedação por testar.
Tampo 18 mm de largura com dois pinos cônicos de encaixe; retenção e dobra dos fios dependem de teste.

Cobertura CO₂ anterior preservada a pedido do usuário; revisão adiada. Sensor interno próximo da lateral eletrônica, referência sem suporte definitivo.

Passagem lateral superior corrigida: Y90/Z125. Bucha e sensor recuados do canto traseiro, com 11 mm até a face interna plana da parede traseira. Sensor de referência em X8..15/Y80..100/Z117,5..132,5; ausência de colisão com a carcaça verificada.

Reorganização v21: tampa única removida para cima cobre a cabeça CO₂, fios e acesso traseiro à PCB. RJ45 e placa permanecem fixos. Tampa do misturador com junta permanece independente. Cobertura de manutenção com duas guias e dois pinos superiores, retenção a testar; retirar antes de inserir as porcas M4 lateralmente.

Acabamento v22: tampa e base lateral alinhadas em X-59, frente Y11 e traseira Y128; topo da tampa em Z150 alinhado ao teto. Junta visual de 0,3 mm sobre a lateral. Painel traseiro com nervura interna; corpo nominal 190 × 141 × 160 mm. Folga para fios sobre a cabeça do sensor segue provisória (altura real pendente).

Junção v23: saia sobreposta de 1,2 mm na tampa desce até Z98; rebaixo correspondente na base, com folga interna nominal de 0,3 mm. Fecha a abertura direta na junção sem impedir remoção vertical. Não é junta estanque.

V24: quatro pinos cônicos Ø3,2 × 2 mm, em retângulo de 26 × 5 mm no apoio traseiro da tampa. Retenção por ajuste e durabilidade ainda exigem impressão de teste.

V25: quatro pinos distribuídos em dois superiores e dois inferiores. Soleira inferior integrada apoia a tampa; corpo 190 × 144,4 × 160 mm. Parafusos das linguetas corrigidos para haste M4 de 30 mm e porca adiantada, sem ponta sobrando atrás do apoio. Peças roscadas continuam ferragens; solicitação de pinos impressos aguarda identificação de dobradiça versus lingueta.

V26: pinos das dobradiças exportados como STL sem alterar geometria. Fechos integralmente impressos com rosca própria Ø8/passo2 e porca impressa em alojamento lateral acessível. Dois pés integrados sob CO₂/eletrônica em Z-10. Bucha do sensor reduzida a Ø16 na aba externa e elevada a Z127,5 para liberar a tampa do misturador. Ensaios de retenção, resistência das roscas/pinos e estabilidade permanecem pendentes.
