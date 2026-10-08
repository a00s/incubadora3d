# Molde e contraforma para inox de 0,3 mm

O macho reproduz o interior do revestimento existente. As duas contraformas
fecham por cima e por baixo dele, apoiando os quatro cantos longitudinais.
A cavidade reserva 0,3 mm para a chapa e mais 0,15 mm por face para ajuste.
Raio do macho: 5,2 mm; raio da cavidade: 5,65 mm; comprimento útil: 109,7 mm.

## Arquivos para imprimir

- [Molde interno — macho](molde_caixa_inox_referencia.stl).
- [Contraforma inferior](contraforma_inox_inferior.stl).
- [Contraforma superior](contraforma_inox_superior.stl).

Há um STEP de cada peça nesta pasta para usinagem ou ajustes.
Os STL já estão com uma extremidade plana na mesa, Z mínimo zero.
As três peças cabem individualmente na K1C com margem de 5 mm.
São ferramentas separadas; não ocupam as 36 bandejas do projeto da incubadora.
A escolha de paredes, preenchimento e material deve considerar o esforço aplicado;
a resistência das ferramentas impressas ainda não foi ensaiada.

## Uso

1. Pré-dobre as laterais da chapa ao redor do macho. O ferramental serve para
   acertar as dobras e os raios de uma chapa já pré-formada.
2. Apoie a contraforma inferior numa placa plana e rígida. Coloque o macho
   com o inox dentro dela e encaixe a contraforma superior.
3. Alinhe os quatro furos Ø6,6 mm. Eles aceitam hastes ou parafusos M6;
   a distância total entre faces externas fechadas é 155,3 mm.
   Se usar parafusos, reserve comprimento adicional para placas, arruelas e porcas.
4. Distribua o aperto com outra placa rígida por cima e feche gradualmente,
   alternando os lados. As faces de encontro das contraformas limitam o fechamento.
5. Abra as metades e retire o macho pela frente. Faça primeiro um ensaio com
   retalho do mesmo inox para avaliar acabamento, folga e retorno elástico.

O conjunto conforma as quatro dobras ao longo da profundidade da caixa.
**O fundo, os recortes e as emendas não são formados por essas peças.**
O revestimento CAD continua sendo uma referência de montagem, não um desenho
planificado de corte e solda. A folga adicional não foi compensada por simulação
de retorno elástico, nem foi calculada uma força de prensa.

## Visualizador

Abra [visualizador.html](../../visualizador.html) e escolha
**Visualizar → Molde e contraforma do inox**. O controle **Abrir contraforma**
afasta cada metade de 0 a 80 mm. Na lista de peças é possível ocultar o macho,
o inox ou cada metade para inspecionar o encaixe.

![Conjunto aberto](preview-aberto.png)

## Regeneração e verificações

Execute `python cad/forming_tools.py` no ambiente com CadQuery e depois
`python cad/build_viewer.py`. O gerador principal `cad/model.py` também exporta
o ferramental. [verificacao.json](verificacao.json) registra os limites e as
verificações de sólidos, interferências e abertura.
