# Preferências do projeto

- Ao iniciar uma tarefa, ler `MEMORIA.md` para localizar firmware, ligações, CAD e validações. Consultar os arquivos locais antes de pedir ao usuário código ou informações já documentadas. Atualizar essa memória quando houver decisões ou observações físicas relevantes; separar relatos, hipóteses e resultados verificados.

- Ao concluir uma alteração autorizada, criar o commit e enviar para `origin/main`.
- Incluir toda peça nova ou modificada no projeto completo `output/incubadora_CrealityPrint_7.2.1.3mf`, além dos STL/STEP e da cópia versionada do 3MF. Preservar as configurações salvas pelo usuário.
- Atualizar o visualizador gerado e a cópia servida em `/tmp/incubadora3d-viewer/index.html`; conferir a resposta do servidor local na porta 8081.
- Conferir geometria, limites da impressora e referências das bandejas antes de enviar os arquivos. Não adicionar arquivos temporários alheios à alteração.
- Porta: imprimir com a frente externa plana na mesa. O layout interno deve ser desenhado para essa posição (+Y do CAD); não resolver problemas das células colocando a porta em pé.
- Montagem física: a pequena borda fina na entrada da porta quebrou. Considerar essa borda ausente em alterações futuras; não depender dela para apoio, fixação ou posicionamento de peças novas.
