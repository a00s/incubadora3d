
## Porta em formato de escotilha — v47

A face externa da porta permanece maior e comprime a junta TPU encaixada
no corpo. A parte interna agora e um painel menor, fechado, com
108,8 × 128,8 mm e cantos R4,4. Ele entra 3 mm na abertura da incubadora,
com folga nominal de 1,05 mm para o inox. O painel e PC rigido, sem junta
TPU adicional na porta. Sua funcao e compor o ressalto da escotilha;
a vedacao permanece no contato dos labios TPU com a face externa maior.

O painel menor trava na porta por duas linguetas flexiveis, sem parafusos,
porcas ou os quatro apoios circulares da v46. Quatro pequenos apoios
retangulares na face posterior guiam a montagem no alojamento cego.
Linguetas: 20 mm livres, parede radial 1,2 mm, deflexao de entrada
nominal 0,3 mm. Os recortes de flexao ficam apenas no painel interno;
a face externa de vedacao continua fechada, com 2,6 mm de material
no fundo do alojamento cego. A retencao e a flexibilidade das linguetas
em PC precisam de teste fisico; nao foram simuladas.

A separacao em duas pecas encaixadas conserva a face plana para imprimir
a porta. O painel menor e impresso com a face voltada para a camara na
mesa, inclusive as linguetas, sem partes flutuantes. Conferir as previas
de camadas e o ajuste antes da impressao completa. As dobradicas continuam
com os M4 × 20 escareados e porcas metalicas solicitados anteriormente;
esta revisao elimina apenas os parafusos extras do painel interno.

Arquivos atuais: `output/v47/`; projeto completo em
`output/incubadora_CrealityPrint_7.2.1.3mf`. O projeto inclui todas as
pecas, molde e amostras em bandejas separadas.

Validacao v47: 59 pares rigidos sem colisao; porta e ressalto conferidos
a 0°, 0,5°, 1°, 2°, 5°, 15°, 30°, 60°, 90° e 110°, com passagem livre
da caixa inox pela frente a 110°. Leitura nativa do 3MF no Creality Print
7.2.1.5476, CLI --info: saida 0, 32 objetos e 32 bandejas; 32 malhas
manifold. Interface grafica e fatiamento nao conferidos.
30 STLs identicos a v46; so a porta e o painel interno foram alterados.
Encaixe das linguetas em PC e estanqueidade ainda exigem teste fisico.
