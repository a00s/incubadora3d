# Mini incubadora CO₂

Projeto de uma incubadora compacta para impressão 3D, com modelo paramétrico
em CadQuery e visualizador HTML interativo. O corpo mede 190 × 141 × 160 mm.
É um protótipo de projeto: o funcionamento térmico, a vedação e o controle
de CO₂ ainda precisam de validação física.

## Imagens

Visualizador com a incubadora fechada e os controles de inspeção.

![Incubadora fechada no visualizador, com controles e seleção de peças](docs/imagens/visualizador.png)

Porta aberta, bandejas retiradas parcialmente e tampas elevadas para visualizar o interior.

![Incubadora aberta com bandejas e tampas afastadas](docs/imagens/incubadora-aberta.png)

Corte das paredes e da porta, mostrando as cavidades internas e a disposição das peças.

![Corte da incubadora com bandejas, compartimentos e paredes com cavidades de ar](docs/imagens/corte-interno.png)

## Como funciona

A câmara contém três bandejas e um reservatório de água. A lateral reúne
o compartimento de mistura e sensor de CO₂ e o espaço da eletrônica.
O gás chega pela conexão de mangueira e passa para a câmara por um furo
interno Ø4 mm. Esse furo não impede o retorno de umidade ao sensor.

A porta usa uma junta TPU, dobradiças e uma lingueta central com pega
para os dedos. O manípulo regula a pressão sobre a junta. As roscas do
fecho e dos parafusos da tampa do CO₂ são integradas à base.
A tampa lateral permite acesso para manutenção; a traseira da tampa e
do corpo termina no mesmo plano. A caixa de alimentação é uma peça removível.

O repositório gera a geometria e os arquivos para revisão e impressão.
Não inclui firmware de controle nem um procedimento de operação biológica.

## Como iniciar

Para visualizar, abra [output/visualizador.html](output/visualizador.html)
em um navegador atualizado. O arquivo já contém o modelo e funciona offline.

- Arraste para girar e use **Zoom** para aproximar.
- Ative **Corte das paredes e porta** e ajuste **Altura do corte**.
- Em **Peças**, selecione componentes ou use **Isolar**.
- Para visualizar a abertura, selecione **Fecho → Afrouxado e girado 90°**
  e ajuste **Abrir porta**. A retirada das bandejas é liberada a partir de 90°.

Esses controles ajudam a inspecionar o desenho; não comprovam o funcionamento mecânico.

## Gerar o modelo e o HTML

Com Python 3.12 e o módulo `venv` disponíveis, execute na pasta do projeto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python cad/model.py
.venv/bin/python cad/check_k1c.py
.venv/bin/python cad/build_viewer.py
```

O gerador faz verificações estáticas de geometria e interferências.
Os testes de movimento ficam desativados por padrão.
O verificador K1C confere dimensões e centraliza cada STL na mesa;
a orientação final e os suportes devem ser definidos no fatiador.

Para acessar o visualizador por outro computador, publique apenas o HTML
em uma pasta dedicada, usando uma porta livre, por exemplo 8081:

```bash
mkdir -p /tmp/incubadora3d-viewer
cp output/visualizador.html /tmp/incubadora3d-viewer/index.html
python3 -m http.server 8081 --bind 0.0.0.0 --directory /tmp/incubadora3d-viewer
```

Acesse `http://IP_DO_SERVIDOR:8081/`. A porta precisa estar acessível na rede.
Se já houver um servidor nessa porta, basta atualizar o HTML servido.

## Arquivos do projeto

- `cad/model.py`: dimensões, peças e verificações estáticas.
- `cad/viewer-template.html`: controles e renderização do visualizador.
- `cad/build_viewer.py`: geração do HTML independente e do fragmento embutível.
- `cad/check_k1c.py`: conferência dimensional dos STL para a K1C.
- `output/v32/`: conjunto STEP, STL por peça, parâmetros e relatórios atuais.
- `output/visualizador.html`: visualizador pronto para abrir.
- [STATUS.md](STATUS.md): situação técnica e pendências do protótipo.

As alterações do projeto podem ser consultadas no histórico do Git.
