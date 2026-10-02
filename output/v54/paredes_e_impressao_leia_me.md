# Paredes e impressão — v54


## Cavidades para carcaça impressa com a traseira na mesa — v54

A carcaça constrói de Y125 para −Y. A grade de 396 pequenas cavidades foi
substituída por 23 cavidades alongadas na camada externa de isolamento:
duas por lateral, duas no topo, duas na base e 15 canais traseiros.
Laterais, topo e base têm somente uma divisória central de 2 mm.
Os canais traseiros não têm divisórias transversais ao longo da altura.

As duas faces da camada de isolamento continuam com 2 mm nominais.
A parede da câmara continua com 4 mm. O fechamento das cavidades acontece
no sentido de construção, com duas rampas a 45° atravessando a dimensão
estreita de 6 mm e uma ponte final de apenas 0,4 mm. Na traseira, o vão
também é de 6 mm na direção de construção; os canais têm até 6 mm de
largura para permitir esse fechamento sem um teto largo sem apoio.
Não foram abertos furos de drenagem nem acesso às cavidades fechadas.

Material sólido da região de isolamento: 541.957,92 → 432.006,24 mm³
(20,29% de redução geométrica nessa região). Essa porcentagem não é uma
estimativa de filamento nem de tempo da carcaça inteira. Os reforços
locais das passagens e as bases maciças dos M4 da caixinha continuam
integrados, com os pilotos cegos e a parede quente de 4 mm preservados.

A porta conserva sua geometria e cavidades anteriores; sua orientação
de impressão segue pendente. A orientação da carcaça está no arquivo
`output/v54/impressao_traseira_na_mesa/corpo_integrado.stl` e no projeto
Creality Print atualizado. Conferir no fatiador que não há suporte dentro
das cavidades fechadas; espessura das linhas, perímetros e configurações
de suporte precisam acompanhar a prévia de camadas. Não há G-code nesta
revisão nem comprovação física de estanqueidade ou impressão sem suporte.

Relatório das cavidades: `output/v54/insulation_geometry_report.json`;
coordenadas das cavidades: `output/v54/body_insulation_layout.json`.


Validação final v54: corpo único válido; 60 pares rígidos sem colisões;
movimentos discretos da porta e da lingueta, entrada do inox, retirada
da caixinha e barreiras maciças dos pilotos M4 conferidos pelo gerador.
As faces inclinadas de todas as 23 cavidades foram verificadas: 45° e
ponte final máxima de 0,4 mm. Todos os 36 STL cabem na K1C com margem
de 5 mm. O projeto 3MF tem escala 1:1 e 36 bandejas; leitura nativa
no Creality Print 7.2.1 terminou com saída 0 e 36 malhas manifold.
Somente `corpo_integrado.stl` mudou: os outros 35 STL são idênticos
aos da v53, inclusive a porta. Volume sólido da carcaça inteira:
1.039.699,88 → 929.166,62 mm³, redução de 10,63% pelo STL.
Essa medida exclui suportes e não é consumo calculado pelo fatiador.
Visualizador WebGL e controles conferidos; sem fatiamento ou ensaio físico.
