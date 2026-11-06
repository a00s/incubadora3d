## ATUAL — duração da resposta sem os intervalos entre doses; gravado às20:41 de2026-11-06

- No log real da revisão c9f8b104, a primeira escada juntou20+40+60ms: comandos em120648/141632/166768ms, vale45733ppm em169044ms e pico52434ppm em231615ms. Ganho120ms/6701ppm correto, mas responseMs usava pico−primeiro comando=110967ms, incluindo46s de espaçamento entre doses. Isso superestimava quanto gás ainda estava em trânsito e atrasava a reposição; leitura ficou~48.5mil depois.
- Corrigido somente o cálculo da duração: pico−ÚLTIMO comando que contribuiu para a escada=64847ms. Chegada ainda medida desde o primeiro comando. Teste reproduz esses números reais e preserva o caso isolado20ms corretamente associado, além de todos os testes da revisão anterior. Não adicionada regra operacional ou desligamento.
- ENVIADO/VERIFICADO f9f1554bf4d13876eb702ab0f2b869a43ee14e0e64d2a4593d4b48065c77dc46 às20:41:30, exit0. Header e0937ed644c574d339ec2f10193b0822a4937e29e0bb02cd82d8b2c373fc35a6.32222Flash/1195RAM;34Flash/853RAM livres. Sketch temperatura.ino permanece898d75c5, sem alterações de EEPROM/porta/temperatura. Não enviadosON/OFF/ACK. Log atual logs/telemetria/usb-20261106T194130-654727Z.log. Confirmar estado pósboot e observar sem novos resets desnecessários.
- Relatório docs/ensaios/co2_duracao_sem_intervalos_2026-11-06.json:2024cenários,567/2000stress travados (antes608). Nominal última hora49070.2–50085.6;frio2000:49136.6–50560.8, pico54475.2;porta49063.5–50071.1,pico51949.5;ruído20:49066.5–50199.6. Troca avisada58217semtrava. Melhorou caso ruidoso e agrupamento; os extremos ainda falham. Não afirmar segurança de qualquer vazão, nem concluir regulação física sem janela real contínua.
- Histórico de aprendizado permaneceRAM, não EEPROM. CO₂/heater desejados continuamEEPROM; reset verdadeiro começa20ms como pedido. Não confundir perda do ganho em reset real com o antigo apagamento indevido ao religar/retomar porta, já removido.

## ATUAL: atribuição das escadas e ganho preservado — GRAVADO2026-11-06 20:33CET

- Objetivo ativo do usuário: corrigir/verificar/upload e manterCO₂ habilitado. Corrigido erro verificado: primeira resposta20ms era atribuída a60msenviadosdepois. Agora fila5comandos associa respostaaoantigosemresposta; subidas podemagruparaberturasquetiveramtempodechegar. Quantidadeesperadaemtrânsitoédescontadadodéficit, sem novo temporizadorfixo: déficitsmaiorespodemreceberdoseapós20s.
- Outraregraindevidaverificada: reset(true), chamado aoON/depoisportaeinvalidez, apagavaganho. Agora preserva1–5referências,arrivalMs/responseMs,lastProbeMs/horário; limpaapenasatribuiçãopendenteetendência. Resetcompletodoprocessadorcontinua20ms/semganho. EEPROMCO₂/heater/portanãofoialterada;nenhumON/OFF/ACKenviado.
- ReposiçãoexplicitadaAOUSUÁRIOANTESdeupload: ritmodsúltimas5aberturas(totalms/tempoatécomandomaisantigo) convertidoem20s eppm pelo ganho, limitada1000ppm. Nãoéaperda80/20×responseMssem limite;estimadorantigoremovidodomodelo. Corteautomatico51000, déficitde recuperaçãoaté50000;pequenareposiçãopoderequereraberturaacima50000dentrodamargem. Mantémmin5/max100ms,aumentomáx20,intervalo20,porta/térmico/trava60000. Nãoadicionadodesligamento. Documentadoem docs/regras_controle_arduino.md.
- ENVIADO/VERIFICADOc9f8b104b98168780374aa9a70d84a2d48ac6516f8f207e8e57afda991179ee7 às20:33:07,exit0. Header9fbc440e9959573b60fcb2b14cd223abd45d459e641d4080327fee8421082f31.32228Flash/1195RAM,28Flash/853RAMlivres. Inteirosdimensionadospormáximosreais:5pendentes<=500ms;cadareferência<=500ms,5ref<=2500ms;produtos<=uint32. Nãoalterarfirmwaresemrecompilar:flashquasecheia.
- Testesfonteinstalada: caso20/40/60→primeirarespostapertence20;gáspendenteimpededupla reposiçãomasnãobloqueiadéficitmaior;ganhoaté5;69ppmruídonãoaprende;20/40/60/80/100cap;+20;reset(true)preservaganhoeON/OFFnãoapaga;rolloverunsigned;proporção20/500→40para1000;legado semhistóriconãoinventamanutenção. Porta/persistência/grandesdeltas/térmico/estatísticaperda/display/painel13/sintaxeJSpassaram. Viewer8081HTTP200/cópiaservidaatualizada,semCAD.
- Simulação2024cenários:docs/ensaios/co2_atribuicao_preservada_2026-11-06.json. Nominalpico52022.2/últimahora49070.2–50085.6;frio2000pico50864.2/49040.2–50036.6;porta51949.5/49063.5–50071.1;pressãometade49018.9–49971.7;dobro49342.7–49829.5;trocaavisadapico58217semtrava. Stress608/2000travas,ruído20últimahoramin48468.2: NÃO validaqualquercilindro/atraso. Usuárioavisadodasfalhasextremasantesdoenvio. Limitesconhecidos:maisde5pendentesperdematribuição;primeiroatrasomedidonãoseadaptaautomaticamente;calibraçãocéga20/40/60aindaexcedecomaltavazão/grandeatraso.
- Lognovo logs/telemetria/usb-20261106T193307-567086Z.log. RetomadaCO₂1/heater1/lock0confirmadaaté24.6s,49553ppm/36.99°C. Produçãoatualc9f8b104supersede96a633ad. Candidataantiga co2_resposta_pendente.hcontinuaensaiorejeitadohistórico, NÃOconfundircomheaderativoagoracorrigidopreservação/tipos. Verificaçãorealemcurso;objetivoNÃOconcluídoatéprovarmanutenção.

## EM ENSAIO OFFLINE: atribuição das respostas; NÃO ENVIADA — 2026-11-06 20:28CET

- Continuação do objetivo: produção permanece96a633ad/commit98161b1, CO₂1/heater1. Telemetriausb-20261106T190848-183482Z.log éBOOT_COUNT2 (conferido), não presumir continuidade do bootanterior6. Até20:27~pico53268, queda47642, retomada49468/6ms, lock0. Corrigido excesso de demanda acima50000, mas manutenção49–51mil NÃO comprovada: oscilação atual aindafora.
- Regressão computacional fonteinstalada: primeirocomando20@120s,40@142s,60@164s; primeira resposta20ms aprendida erroneamente como60ms,1126ppm@190s; pede80ms e depois69, nominal61409.3. Causa adicional concreta: não separa comando recente da resposta atrasada. É erro de atribuição, não prova válvulafechada ou falta degás.
- Candidata SOMENTE OFFLINE firmware/experimentos/co2_resposta_pendente.h: fila5comandos, respostaassociadaaoantigomaisvelho ainda não aprendido, desconta quantidadeprevista em trânsito; primeira chegada/pico estimadas no primeiroresultado; referência até5escadas. Pequena manutençãoexperimental usa média de mscomandados/tempo ×20s, limitada1000ppm, gate51000. Não aplicada àprodução, não deve ser enviada semresolverfalhas. Não é recomendação de nova regra escondida: protótipo rejeitado. Perdas/desligamentosEEPROM não foram mexidos.
- docs/ensaios/co2_resposta_pendente_reprovada_2026-11-06.json registra2024cenários,690/2000stress travados, nominal52022.2pico/49117.3–50045.2últimahora; porta63857.3, trocaavisada63609.4REPROVADAS. Não enviar apenas porque nominal melhorou. Fila5 perdeatribuição quandoatraso temmaisde5comandos; atraso aprendido sóinicial nãoacompanhaalterações; não declararconclusão.
- Ajusteoffline do logdehoje(458amostras/17pulsos): ganho57.37ppm/ms, atraso28s, mistura16s, leak0.0004, RMSEtreino564ppm/holdout1206ppm; não écalibraçãoisolada e erroholdout>1000meiafaixa impede certificarestabilidade. Comparação72cenários porfonte dos6melhoresajustes: instalada0travas/52854.7pico; candidataSEMmanutenção0travas/52471.6,maspioramínimos. Não substituir simulação antiga porajuste novo paraesconderfalhas; ambosconservados no relatório.
- Nenhum novo upload/ON/OFF/ACK nesta continuação. Logger/painelativos e novosdadosverificados. Objetivo continuaATIVO/incompleto; há progresso verificável de diagnóstico econtraprovas, não bloqueioexterno comprovado.

## ATUAL: dose somente pelo déficit — 2026-11-06 20:08CET

- Usuário relatou doses excessivas em equilíbrio, autorizou corrigir/verificar/upload e pediu manter CO₂ habilitado. Confirmado no log anterior:50.890ppm→51ms e50.283ppm→69ms. Causa verificada na fonte: perda estimada×responseMs somada ao déficit, permitindo demanda acima da meta.
- Removida essa parcela da dose. Agora ceil((50000−ppm)×referenceMs/referenceRise), zero a partir de50000. Mantidos ganho observado1–5, início20ms, calibração+20, aumento máximo20, teto100/min5, intervalo20s, EEPROM, térmico/porta/trava60000. Não adicionada regra nova de desligamento. Mudança experimental de agrupamento/atraso foi ensaiada e DESCARTADA antes de compilar/upload: piorou recuperação. Fonte instalada continua referência da última abertura, com sua limitação de atribuição documentada.
- ENVIADO/VERIFICADO96a633adcd009c9a23e877207a1e98cb574475e59af15600fa42cfdeab314e5c às20:08:48, saída0.31886Flash/1179RAM. Header6e6ac178aafeb61c2a873d8324923292c5810fa6ee2599cf9984ca8916a0793c. Boot novo preservouCO₂1/heater1/lock0:37916ppm,36.93°C, conforme EEPROM. NenhumON/OFF/ACK enviado. Log logs/telemetria/usb-20261106T190848-183482Z.log. Coleta e validação física em andamento; não afirmar estabilidade.
- Testes aritméticos incluindo perda150ppm/s×120s e pontos reais50.890/50.283/50000→0,49900→5 passaram; persistência e grandes deltas passaram;13painel passou. Simulação2024cenários preservada em docs/ensaios/co2_deficit_sem_compensacao_2026-11-06.json: nominal61409.3ppm,1075/2000stresstravados. Correção NÃO valida regulação fechada. Usuário informado das falhas antes do envio. O objetivo de funcionamento permanece pendente de prova; não marcar completo pela gravação.
- Verificação física até20:20:32:CO₂1/heater1/lock0;primeira entrada49–51mil em507615ms apósboot; pico51243ppm. Sequência20/40/60/80/68/32/32/18/17/17ms. Ao ultrapassar50000 demanda0, sem desligar habilitação. Depois caiu~48200 e retomou5/24/34ms;última48384. Corrigiu excesso específico neste trecho, mas NÃO comprova manutenção49–51mil: há oscilação e déficit restante. Persistir objetivo aberto; não afirmar funcionando plenamente. Log vivo e serviços ativos verificados.
- Viewer8081 HTTP200/cópia servida atualizada, semCAD/3MF alterados.

## ATUAL: teto100ms por pulso — 2026-11-06 19:28CET

- Usuário definiu que pulso não deve ultrapassar100ms e pediu gravar/Git/testar. Aplicado MAX_PULSE_MS=100 tanto ao resultado proporcional treinado quanto à calibração; mantémmin5ms e aumento máximo20ms.20→40→60→80→100, sem ultrapassar100nas próximas tentativas. Pulsos manuais já estavamlimitados20ms. Não acrescentamos alerta, desligamento ou outro comportamento se a conta pedir>100: só limita abertura.
- ENVIADO/VERIFICADO b24c687a40e87be37b879841beb57fb96d8874ffe31ce2252f1d9728c4825c7a, saída0.32.002Flash/1.179RAM,254Flash/869RAM livres. Hashes completos conferidos. temperatura.ino idêntico à revisão de persistência: não alteramosEEPROM, retomadaCO₂/aquecimento, delta15000 diagnóstico outravasabsolutas. NenhumON/OFF/ACK enviado.
- Testes fonteinstalada:seqlinearaté100 e repetição100,conta enormeclamp100,80→100eapós100permanece100,reduçãopodeir5;4configEEPROM/cicloslógicos/porta;grandesvariaçõessembloqueio.2024cenários afirmam emCADA pulso<=100e aumento<=20. Painel13testes passou. Relatório docs/ensaios/co2_maximo100ms_2026-11-06.json preserva falhas:nominal62237,4ppm,1118/2000stress comtrava60000. Não afirmar5%validado: teto100élimiteexplicitamentepedido, não certificação da regulação.
- Auditoria docs/regras_controle_arduino.md atualizada5–100ms (original1–60, anteriormáximo1000 removido). Logger/painel ativos,uploadmarcadonográfico; viewer8081/cópiaservida conferidos. SemCAD/3MF alterados.

## ATUAL: persistência EEPROM restaurada; removida trava±15000 — 2026-11-06 19:10CET

- DECISÃO EXPLÍCITA DO USUÁRIO: CO₂ e aquecimento devem retomar a última configuração ligada/desligada salva, inclusive após falta de energia, como antes. Não introduzir regras operacionais novas ou exceções de boot escondidas. Solicitou também remover bloqueio por salto15000, pois variação pode ser real. Outras regras foram somente auditadas, NÃO alteradas.
- Removidos macroCO2_EXPERIMENTAL_START_DISABLED e blocos que forçavamCO₂OFF, apagavam retomadaCO₂ da porta e sobrescreviamEEPROM no setup. Ambos os setters já gravambyte29; boot agora só lê. Mantidas travas absolutas/sensores/porta/temperatura, conforme informado. EE atual estavaCO₂0/heat1 por sobrescrita da versão anterior; não escolhemosON nem enviamosON/OFF/ACK. Próxima escolha do usuário será salva e restaurada. Aprendizado continuaRAM, não EEPROM.
- Saltos±15000 agora SOMENTE logam EVENT,co2_fast_change; não desativam, não gravamtrava e não escrevemEEPROM. Interface classifica como informação/controle. Eventos antigos de co2_protocol_jump continuam históricos da versão antiga. Corte≥60000ppm mantém travaEEPROM. Não confundir grande delta com falha comprovada do sensor.
- ENVIADO/VERIFICADO cf89948b0e070b182b2d3743482a6fedb31b727cddf75d0482546569c1055253 às19:10:15, saída0.32.004Flash/1.179RAM (252Flash/869RAM livres). Hashes sketch/modelos/HEX conferidos. Relatório docs/ensaios/co2_persistencia_e_sem_trava_delta_2026-11-06.json. Depois do boot estadoOFF/ON foi restaurado como salvo, sem nova escritaforçada.
- Testes reais extraídos do código:4combinaçõesON/OFF por setters,20ciclos lógicosdeenergia,32estados incluindoporta,bootsem sobrescreverEEPROM e prioridade trava absoluta.400→20000→59000→400 não desliga/não escreveEEPROM;60000 continua desligando/travando. Proporção,max+20,porta,aquecimento e13painel passaram. Renomeado teste debootpara scripts/test_control_persistence.py; removidoantigotestequeexigiaOFF.
- AUDITORIA completa em docs/regras_controle_arduino.md. Importante: limites5–1000ms são de SOFTWARE, não limites físicos comprovados; original7c29d42 usava1–60ms. Ainda existem120s inicial, histórico16leituras≥30s,aprendizado200ppm,platô±2ppm/s,compensaçãodeperda no pedido,resetdeganhoaoON,proteções térmicas eporta. Não fingirque são todaspedidaspelo usuário. Nada dissofoi mudado nesta revisão. Código original usa sensores antigos; não restaurar arquivo inteiro às cegas.
- Logger/painel ativos; viewer8081/cópia servida conferidos. SemCAD/3MF. Preservar responsabilidade de informar regras futuras ANTES de adicioná-las e não sobrescrever a configuração desejada para facilitar testes. RegulaçãoCO₂ ainda semvalidaçãofechada, esta correção não certifica5%estável.

## ATUAL: ganho observado GRAVADO — 2026-11-06 18:37CET

- Usuário pediu explicitamente gravar a correção de ganho. ENVIADO/VERIFICADO faf5aaf8c0e259a7555b71595fa4e4467c59df81dc80c103b7c7ec26303c5fa0, saída0. Hashes de sketch/header/candidata/HEX conferidos contra journal.32.108Flash/1179RAM (148Flash/869RAM livres).
- Instalado código2ea8325: referência só da subida observada, sem somar perda ao ganho. Perda fica separada na necessidade; média1–5,últimaabertura,max+20ms,guardsanteriores preservados. Testes aritméticos e32estados deboot passaram imediatamente antes do envio.
- Boot continua CO₂OFF e preserva aquecimento, conforme informado antes de gravar. Não enviamosON/OFF/ACK nem desbloqueamos. Logger retomado automaticamente; firmware marcado no gráfico. Relatório docs/ensaios/co2_ganho_observado_gravado_2026-11-06.json contémupload/estado e referencia ensaios anteriores.
- Continua EXPERIMENTAL: simulação habilitada dessa lógica já reprovou (nominal62237,4ppm e1184/2000travados). Gravação verificada não é validação da regulação5%. Não orientar ativação automática como se estivesse aprovada. Entrada anterior NÃO ENVIADO agora é histórico, foi supersedida por pedido explícito e envio desligado.

## EM FONTE, NÃO ENVIADO: ganho só da subida observada — 2026-11-06

- Usuário observou estabilização~47mil, mas tempos decrescentes6ms e déficit até50mil. Verificado arquivo boot10:17:43basis124ms/40886ppm;17:59basis67ms/42270ppm. Ganho aprendido subiu329→631ppm/ms, reduzindo aberturas. Outra parte da redução vem da perda estimada decaindo no platô; não confundir tudo com alteração do ganho.
- Erro concreto identificado: atualização17:59 associou8ms a5117ppm, embora subida visível do degrau tenha sido~372ppm. O código somava lossPpmPerSec×tempo à subida aprendida, inflando referência em~4745ppm. Relato de estabilidade é dado útil; equilíbrio entre injeção/perda é hipótese, não prova de passagem física em cada pulso.
- Corrigido APENAS no código: delivered=mass (subida medida), sem somar perda à aprendizagem. Perda continua separada na necessidade da próxima dose. Mantidos últimas1–5,última abertura,global+20,queda/platô eguardas existentes. Unit reproduz372+40×118,625=5117 antigo e exige372 novo; mesmoexemplo67ms/16990ppm,47273ppm,last6ms pede11ms, não5ms da baseinflada42270. Não prometer que próximo pulso físico será11ms, pois estado real de perda/referência pode mudar.
- Testes aritméticos/boot32/porta/aquecimento/perdas/display/12painel passaram; compilou32108Flash/1179RAM. Relatório docs/ensaios/co2_aprendizado_subida_observada_2026-11-06.json conserva falhas:nominal62237,4ppm,1184/2000stress travam60000. Não foi enviado. Arduino continua84ab6cdb, semreboot ouON/OFF/ACK nesta revisão. Código emGit difere do instalado especificamente nesta correção; não dizerque firmware novo foi gravado.
- Motivo de não enviar: não há validação do controle fechado comatraso. Corrigir contabilidade de ganho não comprova5%estável nem resolve atribuição causal de doses sobrepostas. Não esconder falhas nem introduzir pressão/ganho físicos não medidos para fazê-las sumir.

## ATUAL: máximo+20ms global, última abertura e motivo visível — 2026-11-06 16:22CET

- Usuário pediu aumento máximo20ms EM TODAS as doses, não só calibração. Log real foi80→377ms às16:13:44 (não337); leitura atingiu60000 às16:13:59, depois retorno do protocolo. Outro caso15:55:21 teve salto+21893ppm após1000ms em captura anterior. Separar os casos e horários.
- Corrigido next<=lastProbeMs+20; primeiro20; reduções livres, limites5–1000. Corrigida referência: antes atribuía subida5525ppm corrigida a200ms(20+40+60+80), agora usa última abertura80ms desse degrau como usuário pediu. Média ponderada1–5 preservada. Associação causal física ainda não provada; não declarar regulação estável.
- ENVIADO/VERIFICADO84ab6cdb5737cc3b3cb86f27b54e48736487f8cbd23eee717b4efedd4fffac8b às16:22:48, saída0.32.244Flash/1.179RAM,12Flash/869RAM livres. Boot10 arquivo usb-20261106T152300-666503Z.log iniciouCO₂0/aquecimento1/trava1. Depois USUÁRIO limpoutrava16:27:12 e ligoupelobotão16:27:16;log20ms16:27:44. Não enviamosON/OFF/ACK porserial; registrar estado corrente, não repetirqueaindatravado se usuário liberou.
- BootOFFexperimental mantido e agora emite EVT,CO2_BOOT apósBOOT_COUNT. Testes80→raw338 limitado100, próximo<=120, redução5, referência80não200;32estadosboot,porta,aquecimento,perdas,display;12painel/JS. Max+20 validado emCADA comando dos2024cenários. Relatório docs/ensaios/co2_limite_global20_ultima_dose_2026-11-06.json preserva FALHAS:nominal61685,3ppm,1113/2000stress travaram60000. Ainda experimental; não afirmar5%funcionando.
- Painel mostra motivo original e horário no cartão,tooltip,eventos:salto comdelta,≥60000,travarestaurada,porta,comando,botão,proteçãotérmica,bootexperimental. Causa persisteOFF e não é trocada por diagnóstico posterior da mesma trava; limpaquandoON. JSON acrescenta co2_off_reason14/co2_off_at15; anteriores intactos. Chrome conferido:histórico16:13:59 mostraatingiu60000;ao vivo mostrarestaurada16:23:02 enquantoOFF,rawnão validada. Prova /tmp/co2-motivo-bloqueio.png; painel retornouao vivo.
- Gráfico agora reconstrói RETROATIVAMENTE o trecho inicial quando observa volta109→65325 durantequeda: mínimo+65536, sem salto falso0→65mil. É continuidade mínima ESTIMADA, não concentração exata; raw/validade mantidos. Não cruza reinício,porta registrada ou lacuna>10s. ≈e tooltip preservados. Primeirotrecho passa34464bruto→≈100000 após evidência da volta. Não usar estimativa para controle/desbloqueio.
- Logger/painel ativos; viewer8081=200/cópiaservida atualizada. SemCAD/3MF. Flash só12bytes: recompilar toda nova alteração.

## ATUAL: incremento20ms enviado + gráfico de bloqueio — 2026-11-06 15:57CET

- Usuário relatou que dobrar aumentava demais e pediu20/40/60/80... Troca aplicada APENAS à calibração sem resposta útil; depois continua média medida1–5. ENVIADO/VERIFICADO f995720e832dd6a29d139a4e4c429661679ab505fa01eeed514de5da0776ccc4, saída0.32.172Flash/1.179RAM,84Flash/869RAM livres. Boot continua CO₂OFF, aquecimento preservado. NÃO enviamosON/ACK nem removemos trava física/protocolo. Último boot4 restaurou travaEEPROM1; registrar estado real, não afirmartrava0. Log logs/telemetria/usb-20261106T145755-214945Z.log.
- Sequência/reset/proporção e32estados de boot testados. Relatório docs/ensaios/co2_calibracao_incremento20_2026-11-06.json preserva falhas do controlador se ativado: nominal~98465,4ppm,1847/2000 travas. Isso continua EXPERIMENTAL, não afirmar regulação segura/5%estável.
- Usuário pediu mostrar ppm após retorno do contador e região bloqueada vermelha na interface. Parser agora preserva `ppm` válido no índice1 e acrescenta raw_ppm11/display_ppm12/wrap_estimated13. Durante lock usa rawmesmo co2_valid0 para visualização, sem transformar isso em leitura válida para controle. Infere continuidade65536 em saltos maiores que metade do módulo, apenas com trava; reversão reduz offset; resetzeraoffset,portaabertaregistrada interrompe inferência. Lacunas/começo jábaixo não provam voltas anteriores. É ESTIMATIVA, não valor físico exato.
- Gráfico: períodos p8=1 pintadosvermelhos, linha nesse trechovermelha, valores estimados≈ noscards/tooltip/estatísticas; tooltip mostra raw e concentração não confirmada. Escalaautomática semantigo teto70000 que cortava pico. JSON export inclui colunas novas.11testes painel +sintaxeJS passaram; validado emChrome, captura realboot33:65470→785 aparece≈66321, pico≈75396, tooltip≈75302/raw9766. Imagem comprobatória /tmp/co2-bloqueio-grafico.png. Browser usuário ficou nessa captura para revisão.
- Testes isolam começo jábaixo/lock, invalidez preservada, volta/reversão eporta conhecida; reinterpretação sóvisual, não altera firmware/telemetriaoriginal nem envia comandos. Logger e painel ativos; reiniciado painel para invalidarcache. SemCAD/3MF alterados.

## ATUAL: candidata enviada DESLIGADA — 2026-11-06 15:49CET

- Usuário pediu explicitamente enviar. Informado ANTES que seria candidata experimental com CO₂ automático desligado e sem reativação no boot, mantendo aquecimento. ENVIADO/VERIFICADO e8d16f42e6cd7d0c1278ce773d79464834ef38c79559c50e15b5f55e38ea12cc, saída0.32.188Flash/1.179RAM (68Flash/869RAM livres). Novo firmware NÃO foi ativado para injetar e NÃO está validado para isso.
- Modelo instalado é cópia exata da candidata20/40/80... depois média medida1–5, com macro CO2_EXPERIMENTAL_START_DISABLED. Sem800ppm/ms,teto66ms,orçamento59000,timeout ou bloqueio da candidata por dose pendente. Mantidos intervalo20s,subida/platô,noise learning200ppm,supervisor físico51mil/60000,protocolo,sensor,porta e temperatura. Continua teto mecânico1000ms.
- No setup, zera habilitaçãoCO₂ e bit de retomadaCO₂ da porta, salva estado; aquecimento preservado. Isso ocorre em TODO boot, mesmo EEPROMCO₂ON. Verificado extraindo trecho REAL de setup e saveControlState em32combinações. Ativação manual continua possível no código; NÃO recomendar nem comandar enquanto falta validação. Nenhum ON/OFF/ACK enviado por serial; boot fez persistênciaOFF conforme anunciado.
- Testes de sequência/proporção,gates reais,porta,aquecimento,perdas,display,painel passaram. Relatório docs/ensaios/co2_experimental_desarmado_2026-11-06.json conserva reprovação ao simular controlador habilitado: nominal~107706,8ppm e1869/2000 travas. Upload desligado NÃO é aprovação desse algoritmo. Journal agora inclui hash do header candidato de origem além do header instalado/HEX/sketch. Não esconder ensaios nem dizer5%funcionando.
- Após upload conferir amostras: CO₂OFF, aquecimentoON, trava0. Logger/painel ativos; firmware marcado no gráfico. Documento atual supersede entradas antigas de NÃO ENVIADA: foi enviado somente em estado desligado. Sem CAD/3MF alterados.

## CANDIDATA: calibração20ms dobrando; NÃO ENVIADA — 2026-11-06

- Usuário especificou início20ms e dobrar até ver mudança, supondo espaço para preencher. Implementado na candidata offline firmware/experimentos/co2_proporcional_simples.h:20/40/80/160/320/640, teto mecânico já existente1000ms; depois do primeiro resultado útil passa à proporção média1–5. Sem800ppm/ms ou teto66ms. Dose não dobra durante subida relevante, respeita20s e reset volta20. Explicado que ausência de subida também pode ser atraso, não prova espaço livre.
- Teste da sequência, parada durante subida, troca para ganho medido, reset e aritmética passou. Simulação fechada REPROVOU: nominal aproximado107706,8ppm;1869/2000 aleatórios atingem trava60000. Relatório docs/ensaios/co2_calibracao_dobrando_reprovada_2026-11-06.json preserva falhas e hipóteses; não são medições físicas atuais. Não gravar como validado nem repetir versão com excesso conhecido.
- Arduino e produção continuam e91dcb05, sem upload/ON/OFF/ACK nesta tarefa. A candidata não foi instalada. Separar calibração20ms dobrando (pedido agora esclarecido) da atribuição temporal das escadas e gás ainda em trânsito (ainda sem solução validada). Não substituir limites imaginados por outros para fazer testes passarem. Relatório literal anterior é histórico de outro hash, não ensaio da candidata atual.

## CANDIDATA SIMPLES OFFLINE; NÃO ENVIADA — 2026-11-06

- Usuário rejeitou limites/hipóteses não medidos e reiterou a regra simples de proporção1–5, queda/platô e20s. Implementada separadamente em firmware/experimentos/co2_proporcional_simples.h. Produção/Arduino permanecem e91dcb05, sem novo upload ou comando ON/OFF/ACK nesta tarefa. Não fingir que simplificação foi gravada ou que recuperação física foi resolvida.
- Candidata remove800/200ppm-ms, teto59000/orçamento acumulado, bloqueio de dose pendente, janelas extras e timeout. Mantém guarda real51mil e limites mecânicos5–1000ms no modelo; supervisor real do sketch continua com porta/sensor/temperatura/protocolo/warmup. Média ponderada até5 escadas, dose proporcional e20ms antes de existir ganho útil. Subida200ppm é filtro para APRENDER, não trava novas doses. Soma ms de comandos ainda pertencentes à mesma escada. Contadores32bits e produto64bits evitam estouro da conta proporcional.
- Teste aritmético separado passou:20ms→500ppm e déficit1000→40ms; histórico1–5/reset, queda/platô, limite superior, ausência do teto66ms e overflow. Porém ensaio fechado REPROVOU: modelo aproximado nominal pico111008ppm;1803/2000 cenários aleatórios atingiram trava60000. Relatório completo docs/ensaios/co2_proporcao_literal_reprovada_2026-11-06.json. Isso é simulação, NÃO medida da concentração atual nem calibração física. Não gravar candidata ativa com esses resultados. Não substituir hipótese800 por outra escondida.
- Motivo verificável no modelo: repetir doses calculadas pelo déficit enquanto efeito anterior ainda não chegou soma gás; só média1–5 não resolve a atribuição temporal. Uma tentativa offline contando gás pelo ganho MEDIDO melhorou nominal para50185ppm, mas manteve excessos em trocas de cilindro; NÃO foi adotada para não inventar nova lógica sem resolver evidência. Falta uma resposta física isolada ms→ppm nas condições atuais;20/46 recentes não mostraram subida no sensor. Perguntado ao usuário qual dose já teve subida mensurável isolada, sem resposta até esta conclusão.
- Simulador ganhou --model para testar header experimental sem trocar produção; relatório é salvo ANTES de validações, com listas de falhas. --explore preserva falhas de partida em vez de apagar relatório; --require-no-excess ainda reprova excessos. Produção e91 voltou a compilar/ensaiar, hashes idênticos ao upload anterior; não há mudança do sketch ativo. Sem alteração CAD/3MF.

## ATUAL: removido alerta de ausência de subida — 2026-11-06 15:22CET

- Usuário afirmou que NÃO houve injeção apesar dos comandos no log e pediu remover o alerta. Tratar como relato físico; logs confirmam só comandos, NÃO passagem de gás. GPIO7LOW/delay/HIGH ocorre no mesmo caminho de comando, mas não há realimentação da válvula. Não afirmar que a injeção ocorreu nem diagnosticar cilindro/relé/sensor sem evidência.
- Removidos CO2 SEM RESP, EVENT co2_no_response, desligamento180s e congelamento de update/ready por esse prazo. Sem subida não é falha de leitura. Preservadas travas de excesso/protocolo/temperatura/porta e a conta/margem de gás pendente. Se orçamento estiver gasto, novas aberturas ainda podem ser impedidas: não prometer que remover alerta resolve a vazão.
- ENVIADO/VERIFICADO e91dcb05d4ed336f54c9520c7d0ece29411643105a31c354e426223539751872, saída0,31.966Flash/1.175RAM,290Flash/873RAM livres. Habilitação salva preservada; estavaCO₂0 devido ao desligamento da versão anterior, aquecimento1. Não enviamos ON/OFF/ACK nem religamos CO₂ automaticamente.
- Painel sem esse alerta no cartão atual; eventos antigos preservados como desligamento da versão antiga, categoria controle. Testes20milhistórias,10painel,display,porta,aquecimento,perdas,JS passaram.6072cenários,3sementes sem pico≥60000; mantidas falhas de recuperação/pendências, sem garantia5%física. Relatório docs/ensaios/co2_sem_alerta_subida_2026-11-06.json. Hashes e upload conferidos.
- Logger/painel ativos, viewer8081=200, cópiaservida atualizada. Sem CAD/3MF alterados. Relatórios anteriores preservados como histórico, não estado atual.

## ATUAL: recuperação limitada após sonda insuficiente — 2026-11-06 15:12CET

- ENVIADO/VERIFICADO `3ec0f3fe1248d15aecea92aba3857fba4e01d9ef2a2a57adb661432eb435991e`, saída0;32.206Flash/1.175RAM,50Flash/873RAM livres. Preservada habilitação deixada pelo usuário: pós-upload boot4, CO₂1/aquecimento1/trava0. Nenhum ON/OFF/ACK enviado. Logger ativo, novo arquivo logs/telemetria/usb-20261106T141239-906959Z.log; painel reiniciado e HTTP8082/8081=200. Não afirmar estabilidade por ter enviado.
- FALHA REAL VERIFICADA da versão anterior: no log usb-20261106T115244-015856Z, sonda20ms às12:54:47CET a~15986ppm e nenhuma outra por mais2h, leitura~6400. Usuário relatou CO₂ habilitado sem liberar. Causa no código: observing nunca terminava sem subida200ppm. Isso não prova defeito físico;20ms pode não produzir resposta detectável.
- Correção: depois20s normais e duas quedas/platô, resposta insuficiente pode receber complemento dentro da margem de gás ainda disponível, descontando todos os ms pendentes, com envelope≥800ppm/ms e nível inicial preservado. Replay real fornece33ms depois20, total53;6400ppm fornece45ms depois20, total65. Não são doses fixas nem cresce cegamente. Média das últimas1–5 mantém o TOTAL dos ms da escada.
- Correção adicional achada no estresse: primeiro platô podia encerrar só a primeira dose e apagar gás da segunda ainda a caminho (semente20261107/caso47 atingiu77425ppm numa proposta descartada). Conta agora fica aberta até o primeiro platô mais o espaçamento REAL entre comandos; não acrescenta espera fixa60/120s. Referência combinada ou invalidada por reset usa teto alto até obter resposta isolada. Casos47/1497 viraram regressões nomeadas.
- Sem resposta por180s desde última abertura, desliga SOMENTE automáticoCO₂, emite EVENT,co2_no_response,auto_off e visor CO2 SEM RESP; painel marca alerta e explica automático desligado. Oscilações posteriores não apagam falha; botão off/on não apaga gás pendente. Falha exige verificação física antes de novo ensaio; reset físico perde contaRAM. Temperatura/porta/protocolo/EEPROM permanecem. Nenhuma promessa de recuperação se não houver gás passando.
- Testes:20milhistórias, replay real (só admissão, não simula resposta física ao complemento), mínimo20s,proporção,platô,rollover,conta cumulativa,platô parcial,auto-off uma vez,invalidade,reset; porta/aquecimento/perdas/display;10painel e sintaxeJS. Relatório docs/ensaios/co2_recuperacao_sem_espera_infinita_2026-11-06.json com6072cenários/24288h,3sementes:nenhum≥60000,pior56145,9. Ainda há picos>51000 e MUITAS falhas explícitas/recuperação insuficiente. Semente20261106:249/2000>51000,912 não recuperam,1268 sem resposta. NÃO declarar segurança universal nem5%estável. Cenários16000/6400 com tempo morto22ms recuperaram faixa<20min no modelo; isso não é prazo físico validado.
- Para caber no Uno, removido contador legado sem participação no controle e STATUS agora responde STATUS,see_DATA. Estado completo continua em cada linha DATA, mesmas posições. Sem CAD/3MF alterados; visualizador servido atualizado.
- VERIFICADO no equipamento após upload: sonda20ms às15:14:43CET e complemento46ms às~15:15:04CET, total66ms. Portanto a retomada por complemento foi realmente comandada, não só simulada. Ainda observar subida física; comando não prova abertura/passagem de gás.
- RESULTADO FÍSICO VERIFICADO ao fim: apesar dos comandos20+46ms, sensor ficou~5893ppm sem subida útil. Às15:18:04CET emitiu EVENT,co2_no_response,auto_off uma vez; CO₂0/aquecimento1/trava0. Confirmado desligamento explícito após180s, não espera infinita. A correção de sequenciamento está verificada, MAS a passagem de gás/regulação física NÃO está confirmada. Perguntado ao usuário via ferramenta se houve clique/LED do relé, ainda sem resposta nesta conclusão. Não atribuir sem prova ao cilindro/relé/sensor. Não aumentar doses cegamente nem afirmar5%funcionando.
- Persistem relato antigo de wrap do sensor e ausência de confirmação de purga física. Valores baixos não provam concentração segura. Usuário reativou por conta própria antes deste envio; preservamos estado solicitado, sem comandar desbloqueio.

## ATUAL: não sobrescrever dose pendente; enviado12:31CET — 2026-11-06

- GRAVADO/VERIFICADO `fb77319ce92ba9103f214e45a49b9fff462a46707e15ce07c41e835f80726ee4`, saída0.32.224Flash/1.164RAM,32bytesFlash/884RAM livres. Hashes do sketch/header conferidos contra journal e três relatórios simulados. Logger e painel ativos; viewer8081 respondeu200. Firmware marcado no gráfico.
- Correção: ready exige ausência de dose pendente. Uma queda/platô antes da chegada do gás NÃO sobrescreve a observação anterior. reset(true), inclusive desligar/religar ou falha de sensor, preserva uma resposta pendente; reset físico perde RAM. Não há novo temporizador fixo de observação, mas agora espera a subida útil e seu fim. Se não detectar resposta útil, interrompe sequência em vez de repetir cegamente: isso foi explicado ao usuário. Retém média ponderada1–5, sem esperar cinco.
- Necessidade inclui perda no tempo medido do comando até pico da última escada (mínimo20s), em vez de perda20s fixa. Seed20ms, sujeito a limite independente. Limite = margem até59000 / ganho superior: máximo das cinco escadas com hipótese de4×vazão e até8ms de tempo morto; piso200ppm/ms, ou800 sem treino/doses≤8ms. São hipóteses de estresse, NÃO calibração física nem garantia contra pressão arbitrária. Envelope pode limitar demais a recuperação em alguns cenários.
- Replay real20→228ms: agora0ms enquanto resposta anterior pendente; se já resolvida, referência preservada produz raw19ms, limitado10ms pelo envelope. Média não recebe oscilação69ppm como escada útil. Sem respostas não há novas amostras para aprender; não alegar autoaprendizado enquanto desligado.
- Testes passaram:20milhistórias, regressão de dose ainda pendente após54s, proporcionalidade, limite, platô, rollover; porta/desligar-religar sem apagar pendência, perdas, aquecimento, display,9painel e sintaxeJS. Removidos só STATUS humidity_pct (sempreNaN) e pump_wait_cycles (legado) para caber Flash; CSV inalterado.
- Relatório docs/ensaios/co2_resposta_pendente_2026-11-06.json:3sementes,6.054cenários/24.216h, nenhum pico≥60000 ou range_lock. Nominal pico49964,8; frio49986,6. NÃO certifica5% estável: semente inicial329/2000 acima51000,874 não recuperam meta, só40/2000 com última hora inteira49–51mil. Pior pico58038,7. Sem resposta/gás vazio/mau contato pode permanecer sem novas doses. Registrar limitações, não esconder com testes só de segurança.
- Estado pós-upload VERIFICADO:CO₂0, aquecimento0, trava0; leitura23351ppm caindo. Não ativamos nem enviamos ON/OFF/ACK. Persiste ausência de purga ambiente confirmada após wrap anterior. Não orientar ativação baseada apenas no valor atual. Usuário autorizou corrigir/enviar; isso não equivale a afirmar leitura física confiável.

## ATUAL: média das últimas 1–5 escadas — 2026-11-06 12:13 CET

- GRAVADO E VERIFICADO: HEX `7d308dbd3fe7e415bb303b9b7858fcf1b21297aa9d75f8f71b206f4b6702ba82`, saída 0. Flash 32.232 / RAM global 1.164 bytes. Restam 24 bytes Flash e 884 RAM.
- Após reset, primeira sonda 20 ms; depois usa imediatamente as referências úteis disponíveis (1, 2, ... até 5). Ganho ponderado = soma das subidas / soma dos ms. A sexta substitui a primeira. Dose = teto(somaMs × déficit com perda20s / somaPpm), limites físicos 5–1000 ms. Antes de referência útil, ajusta a última sonda pela razão das necessidades, respeitando margem de concentração.
- Subida líquida mínima útil 200 ppm evita aprender ruído como resposta. Replay físico do boot33: oscilação de69ppm não substitui referência25ms/4744ppm; dose calculada19ms, contra228ms da versão anterior. Não há teto percentual de crescimento, nem pausa adicional de observação. Platô em qualquer ppm válido, mínimo20s e travas permanecem.
- CSV mantém posições, mas campos antigos max_rate_ppm_s/uptake_ppm/wait_cycles agora são basis_ms/basis_rise_ppm/basis_steps. Tooltip da dose mostra a base efetivamente usada.
- VERIFICADO após upload: CO₂ automático0, aquecimento0, trava0. Trava já havia sido limpa por botão (ACK registrado); NÃO afirmar que ficou travado. Nenhum comando ON/OFF/ACK enviado por nós. Leitura baixa após wrap não comprova purga; usuário relatou apenas retorno do número. Não orientar reativação com essa evidência.
- Testes: 20.000 histórias numéricas, replay real, média1–5, reset, proporção, platô e rollover passaram;9 testes painel e sintaxe JS passaram. Relatório `docs/ensaios/co2_media_cinco_escadas_2026-11-06.json`:2.018 cenários/8.072h simuladas, com EXCESSOS ainda presentes (nominal ~68.961ppm; frio ~196.644ppm). Média corrige referência espúria específica, NÃO valida segurança sob atraso. Automático deve permanecer desligado enquanto essa limitação existir.
- LoggerUSB e painel continuam capturando; firmware marcado por linha vertical com horário/hash do envio. Viewer8081 respondeu200. Sem alteração CAD.

## ÚLTIMA: platô qualquer ppm + proporção sem teto10% — 2026-11-06

- Usuário pediu agir no platô antes de cair emqualquer valor e rejeitou incrementos
  de4ms causados pelo teto10%. Agora plateauflat>=2 emqualquer leitura válida;
  limite superior51000 e travas permanecem separados. Aprende resultado útil
  também ao estabilizar, não só emduasquedas. Cada dose passa aser observada.
- Retirado teto percentual da conta proporcional treinada. Fórmula inteira
  ceil(msReferencia×(50000−atual+perda20s)/subidaReferencia),5–1000ms. Sondas sem
  resposta útil ainda crescem gradualmente para não dividir porzero. Sem pausa
  deobservação;20s mínimo entre aberturas; aquecimento inicial120s preservado.
- GRAVADO/VERIFICADO: Firmware enviado e verificado · e573e146, saída0.
  HEX e573e14629acb8f61b80c2ead6c552bbe80546b0dc99f20064111cfcd22be860;31.784Flash/1.140RAM.
  Upload anterior9637c33b já tinha platô abaixo49mil, mas ainda teto10%; este o remove.
- Testes exatos de proporção eplatô sem queda passaram,20milhistórias,porta,
  aquecimento,perdas evisor. Simulação atual emco2_plato_proporcao_direta_2026-11-06.json
  registra EXCESSOS GRAVES: modelo nominal~80086ppm,frio~215190ppm. Não omitir essas
  falhas nem declarar regulação segura/estável. Usuário foi informado emcomentário
  que proporção direta com atraso ultrapassou60mil eque trava não recolhe gás.
  Não existe garantia de queplantahipotética reproduz resposta física, mas é risco
  concreto do ensaio computacional; teste éacompanhado pelo usuário nos gráficos.
- Relatórios anteriores preservados. LoggerUSB/painel ativos; envios gravados em
  logs/firmware-events.jsonl, com data/hash/verify e linha no gráfico. Não abrir
  segundo leitor nem enviar ON/OFF/ACK sem necessidade/autorizaçãocorrespondente.

## ATUALÍSSIMO: SEM PAUSA DE OBSERVAÇÃO, gravado às11:30CET — 2026-11-06

- Usuário rejeitou explicitamente a pausa de observação ("nada de pausa") e pediu
  envio imediato para observar gráficos. Retirada TODA espera adicional de60/120s.
  Regra normal:2quedas consecutivas dentro20s ou platô perto50mil com perda medida;
  mínimo20s após fecharválvula. Última dose útil proporcional ao déficit+perda20s.
  Aumento limitado10%,5–1000ms; sem projeção de gás pendente/integral. Somente o
  aquecimento inicial do sensor120s após reboot permanece, informado ao usuário.
- ENVIO CONCLUÍDO E VERIFICADO11:30:18CET, saída0. HEX
  1f436a30e49e66035643ab62650e0dc8d8fdd0aaecf78b116b664eac50fe6e67,
 31.880Flash/1.140RAM. Esta é a última versão; nenhuma outra pendente.
  Arquivo live novo logs/telemetria/usb-20261106T103018-565295Z.log.
  Logger e painel ativos; identificar boot/estado pela captura antes de concluir.
- Versão anterior d8070ed1 tinha observação120s e calibração conservadora: ppm
  caíram para31549. Não foi falta dehabilitação (CO2on1,trava0). Doses20/25/32/40/
 46/49/50 a cada~120s; depois100ms automático em968s. Usuário injetou manual20ms
  em983s e confirmou passagem degás. Sensor subiu31832→32703→33979; não atribuir
  toda subida ao manual, pois100ms automático antecedeu14s. Essa lentidão motivou
  remover observação. Sem novos ON/OFF/ACK. Não afirmar que5% está estável.
- Testes de cálculo, duasquedas20s, ausência depausa,platô,rollover,20milhistórias,
  porta,aquecimento,perdas,visor passaram.6054simulações de4h preservam falhas,
  inclusive excesso/travas em cenários. Relatório co2_sem_pausa_2026-11-06.json;
  versão anterior marcada superseded. Usuário quer acompanhar os gráficos agora.
- PAINEL,marcadores/escala ms,registros automáticos e comandos seguem descritos na
  seção anterior. Não abrir segundo leitor USB. Upload via scripts/arduino.sh
  coordena logger e grava evento vertical real de início/fim/hash/verificação.

## ENTREGA ATUAL: firmware simples + painel + logs automáticos — 2026-11-06

- GRAVADO/VERIFICADO às11:08CET:32.180Flash/1.144RAM, upload saída0; BOOT27,
  CO2habilitado1,aquecimento1,trava0. HEX SHA256
  d8070ed1e6091a0c454c6eeb3b60a43ca53999ce1f76335ca38000250824d682.
  Não há outro firmware aguardando gravação. Comentários posteriores recompilaram
  com o mesmo HEX. Não enviados ON/OFF/ACK. Estabilidade real em5% AINDA NÃO CERTIFICADA.
- Código agora usa última dose útil, duas quedas consecutivas na janela20s e
  proporção ms anteriores×ppm necessários/resultado anterior. Platô perto50mil
  repõe perda histórica, sem precisar esperar queda grande. Piso entreaberturas20s.
  Sem projeção de gás pendente nem integral. Subida observada vale→pico, corrigida
  pela perda medida durante a subida. Calibração começa20ms limitado pela margem;
  janela inicial120s para não atribuir resposta tardia à dose errada. Recuperação
  observa resposta antes de aprender; janela seguinte é o tempo atépico observado
  (20–120s). Platô usa reposições pequenas no mínimo20s. Aumento máximo2×referência,
  duração5–1000ms; histórico de perda preservado ao reabilitar, vazão recalibrada.
- Não afirmar que a regra pura sem observar resposta é segura: protótipo sem essa
  guarda chegou70mil na simulação nominal e NÃO foi gravado. A revisão atual foi
  testada em6054cenários4h/20milhistórias, com falhas de estresse preservadas em
  docs/ensaios/co2_controle_simples_2026-11-06.json. Testes de lógica,porta,perda,
  aquecimento e visor passaram. Não dizer todos cenários aprovados.
- Observação física anterior: boot23(preditivo/piso,limite reduzido40mil) ficou
 39073–44423ppm na última meia hora(mediana40746,5). Boot25(limite48mil) atingiu50917,
  última meia hora46845–50917(mediana48674). Usuário viu a estimativa errada no gráfico
  e pediu a lógica simples. Revisão27 está em calibração/recuperação; manter coleta.
- PAINEL pronto: http://127.0.0.1:8082, arquivos web/co2/, servidor
  scripts/co2_dashboard.py. CO2 + duração comandada/dose emms em escalas separadas;
  pontos coloridos NA CURVA, empilhados, popup afastado do cursor; portas pareadas
  mostram duração emms nos dois eventos, sem inventar fechamento; linha vertical
  de upload confirmado. Zoom,capturas,anotações SQLite,exportação de trecho.
  Estimativa antiga só nas capturas antigas; firmware novo envia coluna legada-1,
  painel não desenha como previsão. Interface não abre serial nem comanda relés.
- COLETA AUTOMÁTICA instalada/habilitada no usuário:incubadora-co2-logger.service.
  Porta estável /dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_2423831353535160E182-if00.
  Processo atual141157,leitor141159(consultar systemctl/fuser antes de confiar emPID).
  Arquivo atual logs/telemetria/usb-20261106T100825-740627Z.log. Cada linha nova tem
  HOST_TIME com horário doPC. Não abrir outro leitor. Serviço respeita porta ocupada,
  espera desconexão/reconexão e guarda cada captura. Coletor manual129385 foi
  encerrado coordenadamente no upload; arquivo antigo /tmp/co2-faixa48... não é live.
- Painel também instalado/habilitado:incubadora-co2-dashboard.service. Comandos:
  scripts/co2_dashboard.sh{install|start|stop|status|logs};
  scripts/co2_logging.sh{install|start|stop|restart|status|logs}.
  Serviços são do usuário:PC/sessão/serviço ativos e caboUSB necessários. Uno não
  temWiFi/Bluetooth integrados. Logs,anotações e diários ficam emlogs/(ignoradoGit).
- Histórico antigo de/tmp/incubadora-telemetria copiado/arquivado emlogs/telemetria;
  backup incremental a cada2s mesmo sem página aberta; proteção contra truncamento.
  Horários antigos estimados; capturas novas têm horárioPC. Eventos antigos próximos
  da leitura seguinte; novos eventos usam horário de recebimento. Oito testes do
  painel passaram. USB automática testada com pseudoterminal, incluindo desligar/
  religar e preservação do arquivo anterior, sem tocar na placa física.
- scripts/arduino.sh upload agora compila, pausa logger, encerra apenas leitor
  conhecido deste projeto, envia --verify, grava início/fim/hash em
  logs/firmware-events.jsonl e retoma logger. Novo upload gera linha vertical real;
  reinício comum continua separado. Primeiro evento conhecido do boot25 tem horário
  explicitamente aproximado. Não usar só BOOT_COUNT como prova de novo firmware.
- Sem mudanças CAD/STL/3MF. Visualizador existente copiado a/tmp/incubadora3d-viewer;
  servidor8081 restabelecido como unidadeincubadora3d-viewer eHTTP200 conferido.

## Controle preditivo + abertura útil — GRAVADO, validação física em andamento — 2026-11-06

- Firmware atual GRAVADO por scripts/arduino.sh upload --verify, saída0:32.254bytes
  Flash/1.152RAM. HEX SHA256 b5ddfdc5ca9fd53cf8917aa16022c6493a5cfd75ff8e94aa39ec08af0e052732.
  BOOT_COUNT23,CO2 habilitado1,aquecimento1,trava0. Não enviados ON/OFF/ACK.
- Coletor somente leitura SEM timeout, sessão45670,PID117995:
  /tmp/incubadora-telemetria/co2-preditivo-piso-20261106.log. Ignorar lixo antes do
  BOOT_COUNT23. Abrir outra serial reinicia o Uno e o warmup120s; não fazê-lo sem
  conferir o proprietário da porta. Upload anterior sem piso foi boot21, log
  co2-preditivo-20261106.log; código anterior31730 emorigin/main era6a15e58.
- Problema físico ainda aberto: anterior não mantinha5%, ficava46–49mil após
  várias dezenas de minutos. Não chamar estabilidade certificada. Revisão atual
  começa39.261ppm depois dos testes e está em calibração/recuperação; monitorar.
- Hipótese agora sustentada por ajuste de4h: resposta aproximadamente linear,
  ganho70,62ppm/ms,transporte54s,mistura4s,perda0,0004/s; holdout cronológico
  último25% RMS838ppm. Não é ensaio isolado de válvula. Scripts/fit_co2_response.py
  reproduz ajuste; relatório co2_modelo_resposta_2026-11-06.json. Isso contradiz a
  atribuição causal antiga de toda subida à última dose e curvas não lineares.
- Novo modelo registra gás comandado60s, projeta concentração, repõe perda20s e
  metade do erro previsto + integral limitada±2000ppm, divide pela vazão aprendida
  e acrescenta trecho inicial de abertura aprendido. Vazão revista100s com variação
  +perda / milissegundos efetivos que passaram pelo atraso. Crescimento25%+5ms,
  quantidade estimada/comando1000ppm perto da meta/5000 abaixo40mil,5–1000ms.
  Calibração começa5ms e tem100s contados da própria sonda; ausência de resposta
  aumenta sonda5ms até100, teto por margem57mil/prior500ppm/ms. Esses limites
  são hipóteses operacionais, não garantia para qualquer pressão.
- Relato/observação: no boot21,5/10ms isolados sem resposta compensada suficiente;
  15ms mostrou captação compensada e23/33/46ms depois produziram subida clara.
  Interpretação: trecho curto de abertura é ineficaz. Aprender piso só em sondas
  isoladas antes do primeiro sucesso; perda de fluxo posterior não o aumenta.
  Excesso>53mil invalida piso. Reset reabilitação/porta/sensor preserva gás pendente.
- Mínimo20s após término mantido, espera durante subida>2ppm/s +memória6s. Retirado
  bloqueio por30s de inclinação antiga e timer20s após pico. Histórico continua
  para visor/perdas. Estados térmicos,botões e travas EEPROM preservados/testados.
  CSV coluna19 chama uptake_ppm (antes dose_rise_ppm); previsão agora real.
- Cinco suites passaram,20mil histórias numéricas, fase da sonda,rollover,porta,
  aquecimento e visor.6048simulações4h: modelo ajustado e estresses, incluindo
  cilindro esvaziando/troca,porta,contato/sensor/tempo morto; MUITOS estresses
  falham, inclusive faixa>60mil com gás pendente. Conservar resultados e limites
  no relatório co2_controle_preditivo_2026-11-06.json, não dizer todos aprovados.
- Tentativas descartadas NÃO gravadas: reforço incondicional do pico baixo
  chegou64mil; preditores grandes/RLS excederam Flash. Versão32254 é a compacta
  com piso; HEX recompilado após comentários permaneceu igual ao gravado.
- Sem CAD/STL/3MF alterados. Visualizador existente copiado para/tmp,8081HTTP200.

## Revisão autônoma: piso limitado e reavaliação com vazão maior — 2026-11-06

- Estado atual GRAVADO:31.730bytes/1.125RAM, upload --verify saída0; código82e0f88.
  BOOT_COUNT19,co2_enabled1,heater_enabled1,range_lock0; leitura inicial53.263ppm
  caindo (ciclo da revisão intermediária), temperatura36,80°C. Sem ON/OFF/ACK.
  Coleta atual somente leitura SEM timeout, sessão76010:
  /tmp/incubadora-telemetria/co2-revisao-autonoma-20261106.log. Não abrir outro leitor
  sem conferir proprietário da porta; abrir serial reinicia o Uno e o warmup120s.
- Piso: só aprende após primeiro sucesso deste boot e com dose sem subida MENOR
  QUE METADE da menor duração já útil. Uma redução moderada com resposta tardia
  não pode virar piso grande. Testes:63ms com efeito/54ms sem efeito→piso0; partida
  com65/72ms sem efeito→piso0. Preservado cálculo pela última dose/déficit inteiro.
- Pico acima51.000ppm descarta piso antigo para permitir aberturas menores quando
  a vazão aumenta. Resposta com duração<=piso também o invalida. Ganho se atualiza
  pela última resposta; não foi fixado manômetro nem uma abertura para esta pressão.
  Caps de ausência de resposta, inicialização e máximo1000ms continuam limitando
  a faixa possível. Sem alteração de PID térmico, portas ou travas EEPROM.
- Cinco testes C++ passaram,20.000histórias, piso, ganho maior/menor, excesso,
  retomada de subidas e rollover. Simulações desta revisão:10.140execuções, duas
  sementes, partida, vazão variável, duas câmaras e comparação sem piso. Caso de
  limiar10ms manteve49.348–50.032ppm na última hora versus46.941–50.188 sem piso;
  caso com queda de vazão49.383–50.096. Muitos estresses falham e não são calibração.
- Relatório co2_manutencao_2026-11-06.json conserva picos intermediários (54.790ppm),
  versões, hipóteses e hashes atuais de ino/header/hex. Estabilidade física final
  prolongada ainda não certificada; deixar aprendizado rodar sem novos reinícios.
  Sem CAD/3MF alterados; visualizador em/tmp atualizado e8081 respondeu200.

## Piso útil aprendido da abertura — gravado em 2026-11-06 (mais recente)

- Na retomada real com a revisão5e69972, após dose produtiva63ms o cálculo voltou
  para7–8ms sem subida mensurável e o CO₂ caiu novamente para47mil. Só aumentar a
  fração do déficit e lembrar subidas não resolve a repetição de pulsos ineficazes.
- Header agora aprende zeroMs a partir de durações sem subida líquida>=50ppm,
  apenas abaixo de uma duração que já funcionou. A duração útil comprovada começa
  desconhecida e só é definida após uma resposta real deste boot/cilindro; depois
  diminui com respostas novas. O valor80ms é apenas referência inicial de dose,
  não uma prova de abertura útil para aprender o piso. Ausência de resposta numa dose
  antes útil não pode inventar um tempo morto maior. Resposta positiva<=zeroMs
  invalida o piso. Reset acompanha reinício/reabilitação/porta/falha de sensor.
- Fórmula: zeroMs+(último_tempo−zeroMs)*déficit/última_subida. Ganho pela última
  dose, sem somar doses. Aumento10% antes do arredondamento, redução imediata,
  caps e guardas anteriores preservados. Piso é empírico da resposta líquida, não
  calibração mecânica isolada; vazão, perdas e mistura podem influenciá-lo.
- Regressão:13ms→2645ppm,8ms sem resposta e déficit500 passa a pedir9ms em vez de5.
  Resposta positiva com7ms zera piso8 antigo. Variação de ganho segue adaptativa;
  não foi usado valor de manômetro nem abertura fixa para a pressão atual.
- Proteção da partida:65/72ms sem resposta antes de qualquer sucesso não aprendem
  piso;80ms→5000ppm depois disso permite16ms para déficit1000, sem piso falso65ms.
- Cinco suites C++ passaram,20.000histórias, invariantes do piso, resposta fraca,
  mudanças de ganho, curva curta e memória/rollover. Build final31.618bytes/1.125RAM.
  Upload com --verify terminou saída0. Sem mudança de PID térmico nem das travas.
- Coletor anterior104678 parado por SIGINT antes do upload. Coleta atual somente
  observação SEM timeout, sessão35097: /tmp/incubadora-telemetria/co2-piso-confirmado-20261106.log.
  BOOT_COUNT17,co2_enabled1,heater_enabled1,range_lock0; leitura inicial43.115ppm,
  temperatura36,74°C. Descartar dados anteriores ao BOOT17. Sem ON/OFF/ACK enviados.
- Mais10.140execuções simuladas: quatro grades da revisão e comparação sem piso,
  com duas sementes, partida, queda de vazão e duas câmaras. No caso de limiar10ms,
  última hora46.941–50.188→49.348–50.032ppm. Caso de queda progressiva de vazão
  manteve49.383–50.096ppm. Muitos estresses ainda excedem ou ficam baixos; não
  declarar tudo aprovado nem manutenção física prolongada em5% confirmada.
- Relatório co2_manutencao_2026-11-06.json conserva as revisões intermediárias,
  pico real54.790, comparações e hashes finais. Verificar estado da coleta atual
  antes de abrir outra serial. Sem CAD/3MF modificados;8081 respondeu200.

## Revisão final após pico real — gravado em 2026-11-06

- Revisão física autônoma encontrou pico54.790ppm na versãobcf2e8e (déficit inteiro
  sem a correção de espera abaixo). Não ocultar esse resultado nem dizer estável.
- Causa verificada no trace: amostras subiram ainda abaixo da concentração anterior
  à dose; uma reversão isolada em289.628ms liberou37ms extras. O timer do pico só
  memorizava máximos acima daquela concentração e esquecia as subidas desde o vale.
- Corrigido: updateCo2RecentRise guarda a última amostra com subida>2ppm/s durante
  avaliação de uma dose. Mantém graça6s antes de reabrir, mesmo que a amostra seguinte
  caia. Nova máxima real continua renovando espera20s, sem encurtamento. Graça curta
  evita exigir20s extras por qualquer ruído. Preservados mínimo20s, dose pela última
  resposta/déficit inteiro, ganho adaptativo, limites, porta, aquecimento e travas.
- Teste reproduz valores/tempos reais277.211/287.561/289.628ms e agora bloqueia o
  comando37ms; testa expiração6s,20s de pico, nenhum vínculo sem dose e rollover.
  Cinco suites passaram, inclusive20.000histórias numéricas. Build31.532bytes/1.121RAM.
- Upload final scripts/arduino.sh upload --verify, saída0. Coletor antigo102666 foi
  parado por SIGINT antes da gravação, sem comandos para a placa. Nova coleta somente
  leitura SEM timeout, sessão1115:
  /tmp/incubadora-telemetria/co2-ajuste-manutencao-final-20261106.log.
  BOOT_COUNT13; co2_enabled1,heater_enabled1,range_lock0, primeira leitura46.529ppm,
  temperatura36,93°C. Descartar dados anteriores ao BOOT13. Sem ON/OFF/ACK enviados.
- Mais8.104cenários finais (duas sementes, perda/vazão variáveis, partida e duas
  câmaras), além dos12.156intermediários. Válvula com limiar manteve49.348–50.032ppm
  na última hora; antes48.092–49.781. Grade constante final181/400 na faixa versus
 170/400, semente separada171/400 versus157/400. Diversos estresses seguem falhando;
  simulação não é calibração e não prova regulação física. Relatório registra pico
  real intermediário, resultados finais e hashes atuais de ino/header/hex.
- Não foi fixado valor de pressão: ajuste continua pela resposta da última dose.
  Caps de ausência de resposta/partida e teto1000ms permanecem e limitam a faixa
  possível; não prometer gás disponível ou vazão arbitrária. Verificação prolongada
  final de manutenção em5% ainda pendente. Sem alterações CAD.

## Ajuste de manutenção e vazão variável — gravado em 2026-11-06

- Relato: mais contínuo/melhor, mas cai47–48milppm. Usuário pediu ajuste de abertura
  e depois autorizou conduzir revisão/gravação sozinho enquanto dorme, considerando
  a variação da pressão com o enchimento do cilindro.
- Evidência: última hora do log antigo teve1.725amostras, mínimo44.363, mediana46.803,
  máximo50.360ppm. Doses produtivas de11/13ms eram cortadas para5–9ms e só depois
  voltavam a crescer, permitindo queda. São respostas líquidas; não diagnosticar
  vazamento físico exclusivamente com a queda do sensor (mistura também contribui).
- Mudança no firmware é uma linha no header: último tempo × déficit INTEIRO / última
  subida, em vez de metade do déficit. Aumento limitado10% antes do arredondamento,
  redução imediata, aprendizado pela última dose. Preservados20s, espera por subida,
  porta, warmup120s, limites/caps de dose, aquecimento e travas persistentes.
- Pressão: continua usando a resposta nova de cada dose, sem valor de manômetro nem
  ajuste para uma pressão fixa. Ganho menor pede tempo maior, ganho maior reduz
  imediatamente. Caps iniciais/sem resposta e teto1000ms ainda limitam a adaptação;
  não prometer funcionamento com vazão arbitrária ou cilindro sem gás.
- Cinco testes passaram, incluindo20.000histórias e exemplos13ms/2645ppm/deficit2137
  (6ms antigos→11ms novos), ganhos decrescentes/crescentes e gates/porta/rollover.
  Build31.432bytes/1.117RAM. Upload --verify terminou com saída0.
- Coleta somente observação sessão55176, SEM timeout:
  /tmp/incubadora-telemetria/co2-ajuste-manutencao-20261106.log. Abrir serial reiniciou
  o Uno: BOOT_COUNT11; co2_enabled1,heater_enabled1,range_lock0; primeira leitura
 43.876ppm e temperatura36,61–36,80°C durante retomada térmica/warmup. Descartar
  linhas duplicadas anteriores ao BOOT_COUNT11. Sem ON/OFF/ACK enviados.
- Observação USB inicial após warmup: doses62 e69ms em sequência, depois aguardou
  a subida sem novas injeções; leitura40.428→47.136ppm de pico parcial. Atribuição
  individual não é calibração isolada. Ainda não comprova manutenção em5%.
- 12.156cenários modelados8h: comparação antes/depois em duas sementes, grade
  anterior de partida e duas câmaras com maior queda/vazão (hipotéticas). No caso
  de válvula com abertura mínima, mínimo da última hora48.092→49.348ppm e máximo
 49.781→50.032; pico transitório50.889 sem mudança. Grade constante dentro da faixa
  na última hora170/400→216/400; semente separada157/400→200/400. Outros estresses
  continuam falhando (excesso ou nível baixo); não declarar tudo aprovado.
- Evidência, comandos, resultados e hashes de ino/header/hex em
  docs/ensaios/co2_manutencao_2026-11-06.json. Regulação física prolongada pendente.
  Sem alterações CAD; visualizador existente atualizado em/tmp e8081 conferido.

## Última dose como referência — gravado em 2026-11-05

- Decisão explícita do usuário: simplificar, aprender pela última dose, repor quando
  estiver abaixo e cair/estabilizar; esperar enquanto sobe; intervalo mínimo20s.
  Usuário autorizou gravação novamente (“manda”).
- Implementado em firmware/incubadora/co2_dosing.h: tempo anterior × metade do
  déficit / maior subida líquida desde a dose; aumento limitado10%, redução imediata.
  Resposta<50ppm aumenta10% sem divisão e sem reset. Sem resposta há teto por
  déficit/150, permitindo até pelo menos80ms depois da primeira tentativa; limites
  gerais5–1000ms. Não soma doses, não usa Padé nem espera adaptativa90–600s.
- Gate real:20s desde fim da injeção,20s sem novo pico, histórico válido, inclinação
  <=50ppm/min e subida recente<=2ppm/s (tolerância ao ruído). Contador30ciclos e
  flag de estabilidade antigos ficam na telemetria, mas não bloqueiam o automático.
  Warmup120s, porta, leitura inválida, cortes e EEPROM continuam preservados.
- Verificado: cinco testes C++ locais passaram, incluindo20.000 histórias numéricas,
  gate exato20s, platô sem precisar cair, subida recente mesmo com média negativa,
  porta, falha, rollover, aquecimento e visor. Build31.444bytes/1.117RAM.
- Upload scripts/arduino.sh upload terminou com saída0 e --verify. Coletor somente
  leitura sessão1377: /tmp/incubadora-telemetria/co2-ultima-dose-20261105.log.
  BOOT_COUNT9; CO₂ habilitado1, aquecimento1, trava0, temperatura36,86–37,05°C,
  leitura inicial41.202ppm caindo durante warmup. Nenhum ON/OFF/ACK enviado.
- 6.063 simulações exploratórias de8h, duas sementes, uma/duas câmaras, partida
 2.000/45.000ppm, porta, pressão, sensor e contato. Os quatro casos de curva medida
  na planta de uma câmara ficaram entre49.879 e50.053ppm de pico; na planta de duas
  câmaras a concentração no sensor difere da principal e alguns picos passam51.000.
  As grades amplas ainda têm excessos e recuperação insuficiente: NÃO afirmar todos
  aprovados nem regulação física estável. Relatório/hashes de fonte/header/hex:
  docs/ensaios/co2_recuperacao_2026-11-05.json. Validação física prolongada pendente.
- Sem alterações CAD; visualizador existente copiado para/tmp e porta8081 conferida.

## Auditoria do simulador e duas câmaras — 2026-11-05 (estado mais recente)

- Relato físico do usuário: resposta inicial pode demorar mais com CO₂ muito baixo,
  na retomada ou após porta aberta, devido à mistura/renovação no misturador e na
  câmara principal. Tratar como relato; volumes efetivos e tempos não calibrados.
  CAD/README documentam sensor no misturador e canal Ø6,2 até a câmara.
- Correção verificada no simulador: atraso zero agendava gás em posição da fila já
  consumida e perdia a dose. Agora entrega no próximo passo (discretização até2s).
  Teste de conservação falha ao restaurar o bug e passa com a correção.
- Tendência/janela de estabilidade passaram a usar o bloco real do firmware;
  histórico reinicia na falha de sensor. Dois tanques opcionais têm concentrações
  separadas, entrada/deslocamento de gás puro e troca conservativa entre volumes.
  Conferidos conservação da troca, entrada zero e limite de gás puro.
- 8.084 cenários exploratórios: uma/duas câmaras, atraso máximo30/300s,
  volumes relativos supostos10%/50%, duas sementes e partida2.000/45.000ppm.
  Resultados/hipóteses/hashes: docs/ensaios/co2_auditoria_simulacao_2026-11-05.json.
  Há excessos em parte dos testes de estresse; NÃO declarar aprovação física.
  O número82.805ppm citado ao usuário veio de atraso hipotético284s, não medido.
- Telemetria preservada: boot5, doses96/122/144ms tiveram subida líquida>=50ppm
  após aproximadamente29,4/10,5/8,5s e picos94,0/77,1/87,6s. Tempos contados desde
  DATA anterior ao pulso (~uma amostra de incerteza). Não equivalem a calibração
  isolada. Doses seguintes e boot7 sem subida líquida; causa não determinada.
- Nenhum upload nesta auditoria. Última gravação confirmada anteriormente foi a
  matemática com proteção de perda de resposta,32.252bytes/1.125RAM. A USB não foi
  aberta agora e estados atuais não foram inferidos. Sem comandos ON/OFF/ACK.
- Firmware candidato NÃO gravado ainda está no diretório de trabalho: mínimo20s
  no gate, mas contador legado30ciclos (~60s) e estabilidade30s continuam limitando
  o automático. Não afirmar que já executa a lógica solicitada de20s/platô.
  Compilação32.250bytes/1.125RAM e cinco testes locais passaram; testes não provam
  estabilidade. Falta ajustar platô e atribuição de doses ainda não observadas.
- Alterações anteriores de firmware/README/testes continuam pendentes no diretório;
  commit desta auditoria contém simulador, relatório e memória. Sem alteração CAD.
  Visualizador copiado para/tmp e servidor8081 respondeu200.

## Recuperação lenta desde~2.000ppm — revisão em bancada 2026-11-05

- Relato novo: CO₂ habilitado na tela normal, após~10min ainda~2.000ppm; usuário
  reconectou USB para revisão/teste. Não é continuação presumida da trava anterior.
- Verificado na USB antes da gravação: leitura válida~1.950ppm,co2_enabled1,
  co2_range_lock0; último pulso20ms sem subida útil. Coleta abriu/reiniciou placa;
  firmware antigo depois emitiu5ms e continuou sem subida. O teste anterior só
  media picos/última hora e começava em45.000ppm: omitia partida realmente baixa.
- Comparação pelo mesmo modelo, semente e planta: desde2.000ppm, nominal antigo
 12.436s→novo2.962s; válvula com tempo morto20ms13.874s→3.208s; vazão alta
 5.054s→2.516s. Isso é simulação (até~50min no nominal modelado), não promessa
  de tempo físico nem prova de solução. Baixa pressão/perda elevada ainda lentas.
- Revisão gravada com --verify e saída0:32.226bytes flash/1.121RAM. Cinco testes
  reais C++ passaram. Sem mudanças no controle térmico, cortes ou trava de faixa.
- Partida sem dose anterior não espera300s além do warmup120s. Abaixo40.000ppm,
  sonda40ms, progressão fraca+20ms e com ganho pode dobrar; >=40.000ppm mantém
  sonda5ms/crescimento5ms. Dose sempre limitada a metade do déficit (1/3 perto).
  Resposta positiva pode reduzir dose mesmo com ganho ainda não validado.
- Somente abaixo40.000ppm, observação pode encurtar para>=90s após subida>=200ppm,
  taxa<=0 e pico sem aumentar há30s. Ausência de resposta mantém300s. Retomada da
  porta/religamento invalida validação anterior e faz nova sonda na faixa atual.
- Removido cálculo de atraso adaptativo que desde a última revisão não era usado
  para decidir espera/dose. Espera de recuperação agora usa a condição real acima.
- Simulações ampliadas:2 grades×2.000 casos (45.000 e2.000ppm),15 casos nomeados
  por grade; comparação com versão a41da6b. Planta de porta agora pausa30s e zera
  duração anterior na retomada como o firmware real. Dois excessos nos1.600 casos
  sinalizados de cada grade; trocas sem pausa têm mais excessos. Muitos casos
  de perda/vazão insuficiente continuam baixos. Todos resultados/limites em
  docs/ensaios/co2_recuperacao_2026-11-05.json; não declarar tudo aprovado.
- Coleta nova somente observação, SEM timeout, sessão77612:
  /tmp/incubadora-telemetria/recuperacao-pos-correcao-20261105.log, BOOT_COUNT3.
  Primeira dose40ms em122.148ms; até261.016ms leitura~1.893ppm, sem subida útil.
  Aguardando próxima dose60ms e resposta; usuário confirmou cilindro/regulador
  abertos, gás e pressão disponíveis. Valor numérico não informado nem exigido
  pelo algoritmo; controle aprende pela resposta, não pelo manômetro.
  Não diagnosticar só software nem afirmar válvula abriu: confirmou-se comando.

## Gravação final confirmada — 2026-11-05

- `scripts/arduino.sh upload` fora do sandbox terminou com saída0 e `--verify`;
 32002bytes flash/1121RAM. Cinco testes de regressão passaram.
- Serial após gravação: BOOT_COUNT3; evento
  `co2_range_lock_restored_after_boot`. DATA:co2_enabled0,heater_enabled1,
  valve_open0,co2_range_lock1; temperatura36,74–36,86°C nos primeiros segundos.
  CO₂ bruto~2290ppm, porém co2_valid0 e sensor em aquecimento: NÃO interpretar
  como concentração física confirmada nem como permissão para destravar.
- Trava persistente preservada, sem CO2 ACK, CO2 ON ou HEAT ON enviados.
  Leitor serial somente observação, sessão13159; verificar se segue vivo antes
  de reutilizar USB. Abrir serial reiniciou a placa. Validar com medição externa
  antes de liberar trava; não declarar regulação física aprovada.

## Revisão ampliada e simulação — 2026-11-05

- Usuário autorizou gravação e pediu milhares de simulações, incluindo troca de
  cilindro e porta. Upload da revisão anterior4381627 retornou saída0 fora do
  sandbox; a placa só é acessível fora do isolamento. Revisão final conferir abaixo.
- Revisão atual: sondas/mínimo5ms; crescimento máximo5ms; espera300s inclusive
  na porta; tendência<=50ppm/min por30s. Ganho maior imediato, menor1/3 por resposta;
  dose de metade do déficit (1/3 perto da meta). Teto1000ms preservado.
- Desligar/religar CO₂, retomar porta, dez minutos sem dose ou falha de sensor
  exigem nova sonda5ms. Falha de sensor reinicia espera300s para não empilhar dose
  cuja resposta ficou invisível. Trocar cilindro usando pausa/desligamento do CO₂;
  sem sinalização, primeira dose ainda pode usar ganho antigo e causar excesso.
- Simulador `scripts/simulate_co2_control.py` extrai seleção de pulso e gates reais
  C++; planta hipotética varia vazão, perda, atraso0–300s, mistura10–120s, ruído,
  falha180s, tempo morto da válvula0–20ms, porta e troca. Semente20261105;
  2.011 cenários de8h (16.088h modeladas). Não é ensaio físico nem calibração.
- Resultado verificado da grade2.000: em1.600 casos sem troca não sinalizada,
  dois picos>51000 (máx51356ppm). Em400 trocas sem pausa,36 excessos. Muitos
  casos de perda alta/vazão insuficiente ficaram abaixo49000. Não declarar todos
  cenários aprovados ou estabilidade física. Relatório com hash e parâmetros:
  `docs/ensaios/co2_simulacoes_2026-11-05.json`. Modelos de casos conhecidos e
  limites de pulso/espera têm asserções; grade exploratória registra falhas.
- Sem alterações CAD. O visualizador foi copiado para/tmp e respondeu200 na8081
  durante a etapa anterior. Não liberar trava de faixa nem forçar controles ON.

## Correção de dosagem CO₂ — 2026-11-05

- Relato: usuário trocou por cilindro com mais CO₂; houve excesso e alerta/parada
  durante a noite. Atribuição ao aumento de vazão é hipótese consistente com o
  relato; não há telemetria desta noite disponível nesta sessão.
- Código verificado: permitia repetir dose em 60 s, compensar perdas projetadas e
  usar todo o déficit na recuperação. Ganho maior era diluído na estimativa antiga.
- Correção local: espera mínima180 s entre doses automáticas, inclusive recuperação;
  usa metade do déficit medido (1/3 perto da meta), sem projetar perdas para dosar.
  Ganho maior é adotado imediatamente; ganho menor decai1/3 por resposta, seguindo
  esvaziamento gradual. Após10min sem dose volta à sonda20ms. Crescimento máximo
 20ms por dose e teto1000ms mantidos; cortes e trava persistente preservados.
- Limitação: sem medição de pressão, a primeira dose após troca durante dosagem
  contínua ainda usa informação anterior. Sonda mínima20ms também exige validação
  com a pressão nova; não afirmar que impede todo excesso.
- Compilação verificada:31892bytes flash,1121RAM. Testes de controle, ganho,
  recuperação da porta, perdas, térmico e visor executados. Sem porta ttyACM nesta
  sessão: NÃO gravado, NÃO retomado controle físico, NÃO validado no cilindro novo.
- Sem alteração CAD ou de peças; STL/STEP/3MF e visualizador preservados.

# Memória local do projeto

## Trabalho ativo — controle térmico e visor, 2026-10-27

Atualização10:26 de28/10: PAUSA explícita solicitada pelo usuário para
colar novamente o metal da porta que se descolou (relato físico). Log
EVENT,door,open, ambos controles0; ALL OFF enviado para confirmar pausa.
Não reativar aquecimento/CO₂ até usuário retomar. Coletor segue ativo.
Supervisor anterior cortou04:21:06 em37,24 °C, perdendo continuidade
noturna. Usuário esclareceu que não quer interrupções experimentais
no computador. `scripts/supervise_temperature.py` agora SOMENTE LEITURA,
sem acesso serial, sem limite térmico/tempo e sem HEAT OFF no encerramento.
Teste com log sintético38 °C e SIGTERM confirmou registro sem desligamento.
Monitor atual sessão87853, estado `observacao-sem-corte.json`, mesmo log
co2-adaptativo. Firmware permanece igual, com corte normal37,1 e emergência39.
Tentativa HEAT ON10:25 foi recusada ERR,DOOR_OPEN; não foi reativado.


Retomada verificada01:20: upload com verificação saída0, BOOT36 após
reabrir coleta. Log atual `/tmp/incubadora-telemetria/coleta-co2-adaptativo-20261028.log`,
SEM timeout; sessão66366. Supervisor contínuo sessão93438, estado
`supervisao-co2-adaptativo.json`, `duration_limit_seconds=null`; ACK HEAT ON
e ambos controles1 confirmados. Temperatura32,61 °C, CO₂~32317ppm.
Câmera ligada ao log NOVO via `observar-co2-adaptativo.py`, sessão91851,
pasta `co2-adaptativo-camera/`; observador antigo parado para não parear
imagens atuais com log velho. Warmup CO₂2min após boot; resposta dos
pulsos >80ms precisa validação física. Metadados/hash em
`docs/ensaios/co2_adaptativo_2026-10-28.json`. Não reintroduzir prazo de
1h no aquecimento nem prazo12h no coletor por padrão.


Atualização01:20 de28/10: usuário pediu aquecimento indefinido SEM limite
de duração; não reintroduzir timeout1h. Supervisor antigo efetivamente
desligou HEAT01:02, não por temperatura. Novo script versionado
`scripts/supervise_temperature.py` sem prazo; conserva corte experimental
37,2 °C e falta de dados. Remover wrapper `timeout` interrompeu coletor,
causando pausa adicional; coleta restabelecida SEM timeout e BOOT34.
Usuário observou CO₂ baixo e suspeita cilindro quase vazio (relato/hipótese).
Verificado: meta50000ppm, leitura~31750ppm, pulsos repetidos80ms; código
limitava toda adaptação a80ms. Correção: teto1000ms, crescimento máximo
20ms por dose também com ganho validado; redução imediata pelo déficit
permitida. Sonda inicial20ms, esperas/intertravamentos preservados.
Cinco testes passaram e build32186bytes flash/1121RAM. Gravação/retomada
conferir abaixo e no log novo. Não atribuir baixa concentração só ao cilindro;
resposta física à correção ainda não validada.


Atualização00:24 de28/10, após retomada do objetivo: supervisor74644 e
coletor70766 vivos; sem EVENT,door desde HEAT ON23:40. Referência37,0 °C
na imagem atual00:23:38, Arduino37,11 °C. Últimos20min Arduino36,74–37,18 °C,
média36,9576 °C;23amostras acima37,1. Não atingiu corte experimental37,2.
O máximo37,18 ocorreu00:13:27; substitui máximos parciais anteriores.
Dados `docs/ensaios/patamar_pote_lado_0024_2026-10-28.json`.
Observador de fotos anterior terminou (PID70767 ausente); coleta retomada
00:23:52 com mesmo script/pasta, índice061 em diante, sessão81596. Serviço
RoomCam segue streaming, quadro0,11s; sem segundo RTSP/inferência.
Teste físico de porta permanece pendente. Supervisor expira~01:02.


Estado00:05 de28/10: teste de abertura solicitado, ainda sem resposta nem
EVENT,door novo. Próximo passo físico indispensável: abertura30s com modo
porta, sem mover água/sondas, e retomada pelo botão. Não inventar execução.
Patamar parcial desde primeira chegada37:12,86min, Arduino36,74–37,11 °C,
média36,921 °C, uma amostra acima37,1; registro em
`docs/ensaios/patamar_pote_lado_parcial_2026-10-28.json`.
Supervisor74644 confirmado vivo00:05; timeout às~01:02 desliga HEAT,
assim como leitura>=37,2 °C/falha de dados. CO₂ permanece habilitado.
Essa interrupção programada não é emergência de firmware39 °C.


Atualização00:02 em28/10: montagem com pote AO LADO, sem contato direto
com aquecedor. Recuperação desde23:40 chegou a37,05 °C às23:52 e máximo
37,11 °C às23:59. Referência37,0 °C às23:55;36,8 °C às00:00;36,9 °C
às00:02. Ensaio parcial arquivado em `pote_lado_antes_porta_2026-10-28.*`.
Supervisor anterior terminou por TRANSFERÊNCIA, apesar do rótulo legado
`released_after_validation`: não significa aprovação completa. Novo supervisor
vivo `supervisionar-porta-pote-lado.py`, PID74644, saída
`supervisao-porta-pote-lado.json`, sessão36062, limite37,2 °C/timeout1h.
Permite pausa pelo botão sem comandar HEAT ON na entrada. Mesmo log e
BOOT33, coletor70766. Não reiniciar serial/firmware durante o teste.
Solicitado ao usuário teste normal de porta30s, sem mover água/sondas;
aguardar confirmação/eventos novos. Câmera observador70767 termina cerca
de00:09; conferir processo antes de continuar coleta de fotos.


Atualização após manutenção do ventilador (~23:40): usuário confirmou serviço
feito e porta fechada. ALL OFF foi enviado para manutenção; portanto essa
retomada parte da integral inicial, não é teste isolado de pausa de porta.
Relato físico NOVO: pote agora AO LADO do aquecedor, sem ficar sobre ele;
usuário descreve aquecimento indireto pelo piso de alumínio. Substitui a
montagem anterior de canto encostado. Não presumir volume restante nem RH.
Sem novo ajuste de firmware/offset nesta mudança. CO₂ habilitado confirmado
na telemetria; retomada térmica supervisionada por
`/tmp/incubadora-telemetria/supervisionar-pos-ventilador.py`, saída
`supervisao-pos-ventilador.json`, usando o mesmo log calib-agua25/BOOT33.
Conferir estado vivo antes de afirmar que continua aquecendo.
Etapa anterior foi interrompida pela manutenção, não por limite térmico:
máximo Arduino37,11 °C; referência atingiu37,0–37,1 °C nas capturas.
Esses dados não validam a montagem nova nem uso com células.


**Estado ~23:11: ensaio vazio, sem células (relato do usuário). NÃO aprovado
para uso com células; controle térmico ainda tem picos e diferença entre sondas.**

Resultados verificados: a revisão de tendência filtrada, gravada ~17:29,
falhou no ensaio supervisionado às 17:42 (37,20 °C, HEAT OFF confirmado).
O controle foi reabilitado posteriormente, sem novo ACK serial; origem não
estabelecida. Entre as leituras das horas seguintes, Arduino atingiu 37,45 °C.
Às 22:01:32, câmera atual mostrou referência37,9 °C e Arduino~37,0 °C.
Não atribuir todos os picos à calibração. Arquivo completo, parâmetros e
patch reprodutível do firmware realmente ensaiado em
`docs/ensaios/filtro_tendencia_2026-10-27.{csv,json,patch}`.
Etapas anteriores, incluindo recuperação com pico37,39 °C, também arquivadas.

Relato físico do usuário ~22:11: recipiente estava SECO; porta foi aberta,
fechada e adicionados25mL em OUTRO pote, com apenas um canto tocando o
 aquecedor. Usuário pediu manter exatamente assim por enquanto e comparar
sem contato depois que estabilizar em37 °C. Não alterar essa montagem sem
nova orientação. Evaporação/umidade dessa montagem ainda não medidas.
Hipótese: secagem e contato térmico mudam a carga térmica e a evaporação;
isso não é explicação verificada de todos os erros do controle.
Arduino NÃO mede atualmente umidade da câmara (`rh_pct=nan`); DHT22 mede
somente temperatura da eletrônica. Os95% citados pelo usuário são relato
anterior, não leitura presente da telemetria.

Firmware atual gravado e verificado ~23:09: TODOS os cinco campos numéricos
(CO₂, temperatura da câmara, temperatura interna, ppm/min, cm³/h) usam cache
por caractere. Só apaga a célula cuja forma mudou; mudança apenas de cor
repinta sem apagar. Fonte grande tem avanço13px, pequena7px, confirmado
pela decodificação das fontes reais no teste. Campos encurtados apagam sufixos.
Visor verifica atualizações ~640ms durante atendimento de entradas, fora da
espera2s do ciclo de CO₂; sensor DS18B20 converte em >=800ms. O CO₂ continua
lido no ciclo principal. Testes de todos os cinco campos, mesma leitura sem
SPI, cores sem apagar, mudança de comprimento, cadência e modo porta passaram;
também passaram os quatro testes térmico/porta/CO₂. Flash32160bytes, RAM
estática1121bytes. As alterações gráficas não mudaram ganhos/cortes. Depois delas houve somente
o ajuste operacional de offset abaixo.

Hardware confirmado pelo usuário em imagens de anúncios: tela AZDelivery
1,77pol ST7735(S),128×160,SPI, com conversor TXS0108E. Driver configurado
Ucglib_ST7735_18x128x160_HWSPI corresponde à família. Fichas oficiais:
https://www.az-delivery.de/en/products/1-77-zoll-spi-tft-display e
https://www.ti.com/product/TXS0108E . CSV documenta VA3,3V/VB5V, A→tela,
B→Uno, OE via resistor aVA. Qualidade elétrica não medida. Fontes AZ têm
especificação2,7–3,3V e diagrama de ligação do módulo com VCC5V; identificar
versão/regulador da placa antes de recomendar mudança de alimentação.
O intervalo de ~2,35s no desenho antigo foi medido no log e explicado pela
espera do programa; não atribuir automaticamente a driver/conversor.

Ajuste operacional gravado23:09: offset de+1,575 para+1,175 °C (−0,4 °C).
Base: últimos10min antes da interrupção tiveram média36,965 °C no Arduino,
faixa36,83–37,14 °C; referência repetiu36,5–36,6 °C nas imagens23:00/23:06
e anteriores. Fonte/dados em campos_parciais_antes_offset_2026-10-27.*.
É alinhamento operacional do ponto de referência desta montagem: referência
apoiada em metal, Arduino livre no ar; NÃO calibração comum de ambos sensores.
Ainda precisa validação independente no novo patamar e pico. Ganhos, período,
corte normal37,1 °C e emergência travada39 °C mantidos. Todos os testes passaram.

Coleta viva: `/tmp/incubadora-telemetria/coleta-calib-agua25-20261027.log`;
fotos/metadados em `calib-agua25-camera/`; BOOT33 (descartar trechos pré-boot).
Supervisor `supervisao-calib-agua25.json`, script `supervisionar-calib-agua25.py`.
Retomada automática do ensaio confirmada23:10:10 após20s de dados contínuos.
Às23:11, Arduino36,24 °C, ambos controles habilitados, aquecedor pulsando;
queda inicial inclui mudança do offset e interrupção para gravação.
Supervisor interrompe aquecimento a37,2 °C, falta de dados ou timeout1h
(após retomada, aproximadamente00:10). Verificar PID vivo e dados atuais.
CO₂ ativo. Manter25mL, só o canto do pote tocando e mesmas posições de sondas,
conforme pedido do usuário. Não declarar calibração/controle aprovados antes
 de comparar novo patamar e pico completo da referência e do Arduino.
Dados/limites e hashes em docs/ensaios/calibracao_operacional_agua25_2026-10-27.json.

Gravação da cadência foi autorizada pelo usuário ~22:30; ensaio anterior
interrompido com35,33 °C, não por falha térmica. Etapa seguinte interrompida
~22:41 para atender pedido de estender redesenho parcial a todos os campos,
com máximo36,76 °C. Não confundir interrupções gráficas com ensaios aprovados
ou com falhas por temperatura. Arquivos `agua25_pre_cadencia_2026-10-27.*`
e `visor_rapido_2026-10-27.*` preservam dados e fonte realmente gravada.

Câmera foi reposicionada; imagem atual está legível. Usar quadro inteiro
após mudanças; recorte antigo x640–905 não enquadra mais todos os dígitos.
Referência25,3 °C observada22:12:25 durante manipulação/reset. Usuário
anunciou reset de mínimo/máximo; confirmação visual dos novos extremos
pendente. Não adivinhar dígitos pequenos. Serviço existente127.0.0.1:8766;
não iniciar segundo RTSP, não mover PTZ nem expor configuração/credenciais.
CAD/STL/STEP/3MF sem mudanças; visualizador deve seguir servido em8081.

Este arquivo orienta sessões futuras. Conferir o código atual antes de assumir que
parâmetros aqui registrados continuam iguais. Não presumir que o firmware local
é idêntico ao gravado na placa sem verificar a gravação.

## Onde procurar

- `AGENTS.md`: regras de trabalho, entrega e restrições físicas.
- `README.md`, seção “Controle do Arduino pela USB”: sensores, ligações,
  calibração, comandos, telemetria e procedimento de compilação/gravação.
- `temperatura.ino`: fonte principal do Arduino, controle térmico/CO₂,
  leitura dos sensores, display, botões e modo porta.
- `firmware/incubadora/incubadora.ino`: link para `../../temperatura.ino`,
  não é um segundo firmware. `display_font.h` fica nessa pasta.
- `scripts/arduino.sh`: setup, compile, upload e monitor; padrão Uno R3,
  `/dev/ttyACM0`. Gravar reinicia/interfere no controle físico: não fazer
  automaticamente durante uma investigação apenas documental.
- `scripts/capture_serial.py`: captura da telemetria serial a 9600 baud.
- `scripts/test_heater_control.py`, `test_door_recovery.py`,
  `test_display_door.py`, `test_co2_control.py`, `test_co2_loss.py`:
  verificações do firmware; não substituem ensaio térmico físico.
- `arduino-libraries/NDIRZ16`: biblioteca local do sensor de CO₂.
- `cad/model.py` e demais scripts em `cad/`: fontes e ajustes do projeto 3D.
- `STATUS.md`: histórico técnico, estado geométrico e pendências físicas.
- `output/v59/`: STL/STEP, cópia versionada do 3MF e relatórios atuais.
- `output/incubadora_CrealityPrint_7.2.1.3mf`: projeto completo salvo pelo usuário;
  preservar configurações. `output/visualizador.html`: visualizador gerado;
  cópia servida em `/tmp/incubadora3d-viewer/index.html`, porta 8081.
- `Incubadora CO2 - CO2.csv`: tabela de ligações/pinagem dos componentes
  (começa pelas conexões da tela); consultar junto ao firmware para o esquema.

## Controle térmico conferido em 2026-10-27

- Câmara: DS18B20 em D4; eletrônica: DHT22 em D2; aquecedor em D6,
  saída ativa em LOW. Ligações detalhadas no README e no firmware.
- Meta 37,0 °C; offset aplicado na aquisição `+1.175 °C` (ajustado e gravado em 2026-10-27;
  validação térmica em andamento).
  O README registra o contexto e a posição diferente da referência.
- Pulsos atuais: até 17 s em toda a faixa, sem teto diferente perto da meta;
  pelo menos 20 s entre inícios e 3 s desligado. Tendência em janelas de 30 s;
  integral limitada a 17 s. Kp atual 9.000 ms/°C, Ki 1.000 ms/(°C·min),
  Kd 18.000 ms/(°C/min): aproximadamente 120 s de antecipação.
- `controlHeater` contém o PID e os cortes; `toggleDoorMode` pausa e
  restaura os controles. Conferir os nomes no código se forem refatorados.
- Pausa de porta preserva integral aprendida na RAM e invalida tendência;
  desligamento manual/falhas restauram a estimativa inicial de
  10.000 ms/20 s (50%) de manutenção, com base no histórico observado.
  A integral cresce só com tendência pronta, |taxa| <0,15 °C/min e saída não saturada;
  erro negativo a descarrega. PI/D atua nos dois lados da meta até corte 37,1 °C.
  Não há gravação desse aprendizado na EEPROM.
- README descreve os parâmetros do controle;
  para parâmetros executados, conferir as constantes e a lógica do firmware.

## Relato físico de 2026-10-27 — investigação pendente

- Usuário relata estabilidade na noite anterior; depois Arduino em 37 °C
  e referência inicialmente em 37,4 °C, chegando a 37,6 e 37,8 °C.
- Esclareceu que a subida ocorreu após abrir a porta e retomar o controle;
  a temperatura também baixa. Não tratar como mero offset constante.
- Vasilha sobre o aquecedor na parte inferior: 10 mL colocados à noite
  estavam esgotados pela manhã; depois acrescentou 50 mL. Não há horários
  e pesagens suficientes para calcular evaporação diária.
- Água e abertura alteram a carga térmica. Inércia e comportamento do PID
  são hipóteses a verificar com telemetria, não conclusões comprovadas.
- Ainda faltam leituras simultâneas dos dois sensores, estado do relé e
  curva temporal durante a recuperação. Nenhuma calibração ou lógica foi
  alterada nesta atualização da memória.

## Restrições físicas essenciais

- Borda fina da entrada da porta quebrou; não depender dela para peças novas.
- Porta se imprime com a frente externa plana na mesa (+Y do CAD para cima).
- Alterações de peças exigem STL/STEP, ambos os projetos completos 3MF,
  visualizador e verificações descritas no AGENTS.md.

## Câmera e coleta — 2026-10-27

- Acesso autorizado à câmera apontada ao termômetro: projeto
  `/home/x/projetos/acessocamera`; ler seu `AGENTS.md` antes de usar.
- Serviço existente: `http://127.0.0.1:8766`; cliente
  `/home/x/projetos/acessocamera/.venv/bin/roomcamctl`.
  Consultar status/frescor e capturar sem mover a câmera. Não ler nem expor
  `camera.local.json` ou linhas de comando RTSP que contenham credenciais.
- Visor principal: referência atual; mínimo à esquerda e máximo à direita,
  conforme usuário. Só transcrever números realmente legíveis.
- Usuário trocou o pote por placa de Petri mais baixa e de maior superfície;
  volume não informado. Relatou pouca perda no µ-Slide durante a noite,
  apesar de o reservatório secar; contribuição das tampas e da umidade é hipótese.
- Posição esclarecida pelo usuário: sensores separados por aproximadamente
  3 cm; referência apoiada na gaveta metálica, sonda Arduino pendurada livre
  no teto. A referência sofre influência térmica do metal e a sonda mede o ar;
  proximidade não garante igualdade durante transientes. O ajuste atual busca
  a temperatura da referência na região das amostras, não uma calibração
  metrológica intrínseca da sonda. Não mover sensores durante a comparação.
- Coleta anterior: `/tmp/incubadora-telemetria/coleta-20261027.log`.
  Após gravação: `coleta-pos-ajuste-20261027.log` na mesma pasta.
  Anotações e imagens temporárias nessa pasta; não presumir que sobreviverão
  a reinicializações. Conferir processo e data do log antes de afirmar coleta ativa.
- Abertura/fechamento para trocar água foram confirmados por toque longo;
  referência 33,4 °C versus Arduino 34,08 °C às 09:49, durante recuperação.
- Às 12:24–12:28, referência visual 36,2–36,3 °C; Arduino na última hora
  média 36,9707 °C, mínimo 36,76 e máximo 37,14 °C.
- Correção inicial de offset −0,75 °C (+2,325 → +1,575), compilada,
  testes do firmware aprovados e upload verificado por saída 0 às ~12:30.
  Ainda requer observar equilíbrio e recuperação; não declarar problema resolvido.
- Autorização do usuário: corrigir temperatura e fazer testes; pedir abertura
  física da porta quando necessário. Não abrir serial em paralelo ao coletor.
- Abrir serial pode reiniciar Uno; houve reinício na conexão inicial e após
  retomar coleta. Salvar aprendizado/estatísticas em EEPROM ainda não implementado.
- CPU: análise de objetos RoomCam desligada via POST `/api/vision/stop`
  com JSON `{}`; vídeo permanece disponível. Só fotos não exigem inferência.
  `roomcamctl vision stop` retornou 404 nesta sessão, usar API se necessário.
- Coletor serial corrigido com `select.select`: de ~100% para ~0,1% CPU.
  Teste com pseudoporta verificou espera ociosa e preservação de bytes.

Acompanhamento inicial após ajuste: referência 36,5 °C às 12:35:40,
36,7 às 12:36:40, 36,8 às 12:37:40 e 36,9 às 12:39:40;
Arduino pareado em 36,83 / 36,95 / 36,89 / 36,95 °C, respectivamente.
Ainda não é comprovação de equilíbrio prolongado nem do teste de porta.
Capturas pareadas em `/tmp/incubadora-telemetria/pos-ajuste-camera/`,
metadados em `observations.jsonl`. Coleta de imagem limitada a uma hora,
sem inferência local de objetos e sem mover PTZ.

## Falha observada e correção da aplicação do PID — 2026-10-27

- Teste solicitado: abertura física de ~30 s, sem mover água/sensores;
  usuário confirmou execução. Modo porta ficou pausado ~57 s: abertura entre
  ms 883662/886129 e fechamento entre 940321/942611 no log pós-calibração.
- Arduino chegou a 33,39 °C após fechar. A referência voltou a 37,0 °C
  às 13:00, mas às 13:04 marcou 37,3 °C; Arduino atingiu 37,51 °C,
  já com aquecedor desligado, e depois caiu a ~36 °C.
  Logo, o primeiro ajuste de offset não resolveu a oscilação. Não declarar
  aquele teste aprovado nem usar somente a passagem por 37,0 como estabilidade.
- Problema encontrado na aplicação: duração do pulso com apenas 3 s de pausa
  torna a potência não linear: 12/(12+3)=80%, 6/(6+3)=67%.
- Nova versão gravada ~13:11: período mínimo de 20 s entre inícios,
  até 17 s ligado (85% longe da meta) ou 12 s (60% perto); Kd de 6.000
  para 18.000 ms/(°C/min). Antiwindup considera o teto ativo de cada faixa.
  Offset permanece +1,575 °C; Kp, Ki, corte de 37,1 e emergência de 39 °C preservados.
- Teste da função C++ real verificou 6 s ligados a cada 20 s durante seis
  períodos: exatamente 30% de tempo ligado, mantendo cortes e pausas.
  Compilação/upload saída 0, 32.166 bytes Flash e 1.012 RAM estática.
- Coleta nova: `/tmp/incubadora-telemetria/coleta-periodo20-20261027.log`;
  imagens/metadados em `periodo20-camera/`. Houve reinício no começo da
  coleta (BOOT_COUNT 6); desconsiderar trecho inicial truncado e confirmar
  continuidade de ms e ausência de novos boots antes de avaliar a estabilidade.
  Verificação física desta versão ainda pendente.

Refinamento ~13:23: removido o teto por faixa de 12 s/60%, que limitava a
aproximação com demanda saturada perto de 36,7 °C. Limite único de 17 s/85%
e integral máxima de 17 s, preservando período de 20 s e Kd de 18.000.
Compilação/upload saída 0: 32.122 bytes Flash / 1.012 RAM estática.
Coleta atual em `/tmp/incubadora-telemetria/coleta-pid-linear-20261027.log`,
quadros em `pid-linear-camera/`. As pastas `pos-ajuste-camera` e
`periodo20-camera` documentam etapas anteriores, não a versão atual.
Validação física do limite único ainda pendente; não declarar estabilidade
pela passagem momentânea por 37 °C. Confirmar boot e continuidade do log.

## Versão PI/D de manutenção — gravada ~13:52 em 2026-10-27

- A versão de teto único ainda oscilou: depois de capturas em 36,9–37,1 °C,
  às 13:44 a referência caiu a 36,2 °C e o Arduino a 36,08 °C.
- Removido o corte total da demanda logo acima de 37,0 °C. O PI/D deve
  equilibrar perdas também levemente acima da meta; corte independente 37,1 °C
  e emergência 39 °C preservados.
- Ganhos atuais e manutenção inicial descritos no topo. A integral não carrega
  com o grande erro da abertura e fica preservada durante a pausa de porta.
- Testes da função real verificam manutenção em 37,05 °C, corte em 37,1 °C,
  retenção de integral ao pausar/retomar e duty de 30% para 6 s/20 s.
  Teste dos botões verifica também retenção de 11 s de integral no toque longo.
- Compilação/upload saída 0: 32.204 bytes Flash / 1.012 RAM estática.
- Usuário confirmou mínimo/máximo zerados e segunda abertura de ~30 s,
  com os toques longos. Essa execução coincidiu com a gravação/reabertura
  da serial: o registro não separa a recuperação da porta do reinício.
  Não pedir nova abertura agora; acompanhar primeiro esta recuperação.
- Coleta atual: `/tmp/incubadora-telemetria/coleta-pi-manutencao-20261027.log`;
  imagens/metadados: `pi-manutencao-camera/`; observador temporário
  `observar-manutencao.py`. Confirmar processos/frescor antes de continuar.
- Início às ~13:53: Arduino 34,33–34,51 °C, referência visual 35,4 °C;
  ambos os controles habilitados. Validação física desta versão ainda pendente.

## Aprendizado somente em temperatura lenta — gravado ~14:19

- A etapa anterior também falhou: pico de 37,64 °C no Arduino e máximo
  visual de 37,2 °C na referência; depois caiu a 36,1 °C na referência.
  O primeiro patamar em 36,9 °C não comprovou estabilidade.
- Integral positiva agora aprende somente com tendência pronta e
  |taxa| <0,05 °C/min, em qualquer distância da meta, com saída não saturada.
  Durante aquecimento/resfriamento rápido, mantém a estimativa de perdas.
  Erro negativo ainda descarrega a integral. Ganhos 9.000/1.000/18.000,
  período 20 s e teto 17 s preservados; PI/D segue ativo até corte 37,1.
- Inicialização e resets usam 10 s/20 s (50%); pausa de porta preserva o valor
  aprendido na RAM. Não há gravação do aprendizado em EEPROM.
- Testes reais verificam aprendizado de perda estacionária em 36,3 °C e
  congelamento da integral com tendência de +0,2 °C/min, além das verificações
  anteriores. Compilação/upload saída 0: 32.234 bytes Flash / 1.012 RAM.
  Restam só 22 bytes de Flash no Uno: recompilar qualquer alteração futura.
- Coleta atual: `/tmp/incubadora-telemetria/coleta-aprendizado-estavel-20261027.log`;
  imagens/metadados: `aprendizado-estavel-camera/`, observador `observar-estavel.py`.
  As demais pastas são ensaios anteriores. Validação física atual ainda pendente.
- Usuário confirmou mais um reset de mínimo/máximo após a gravação desta
  revisão, por volta de 14:22, sem abrir a porta. Usar esse registro para o pico atual.
