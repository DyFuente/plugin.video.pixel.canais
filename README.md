<h1>Canais Pixel</h1>

Mod do addon TIABET do leandrotsampa

- Adiciona picons dos canais
- Cria grupos de canais
- Oculta canais que iniciam com PG-
- Oculta canais informativos

Link para download:
https://github.com/josemoraes99/kodirepo/raw/master/plugin.video.pixel.canais/plugin.video.pixel.canais-1.0.8.zip


<h2>Instalação</h2>

- Abrir o Kodi >> Sistema >> Add-ons >> Instalar a partir de um arquivo ZIP
- Procurar o arquivo plugin.video.pixel.canais-1.0.8.zip

<h2>Utilização</h2>

- Abrir menu principal > Video > Add-ons
- Escolha Canais Pixel
- Escolha a opção desejada (pode ser mais que uma)
- Reinicie o Kodi para aplicar

<h2>Se faltar algum picon</h2>

Consultar o arquivo no Media Player do Pixel:

/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/userdata/addon_data/plugin.video.pixel.canais/pics_nao_encontradas.txt

Copie desse arquivo os canais que faltam e coloque no grupo do Whatsapp ou no forum

<h2>Utilizar picons próprias</h2>

É possível utilizar imagens personalizadas

- Abrir menu principal > Sistema > Add-ons > Meus add-ons > Add-ons de Vídeo > Canais Pixel > Configurar
- É possível escolher entre um endereço local ou web
- Se escolher web é necessário a url completa (incluindo http ou https)
- As extensões dos arquivos podem sem .jpg ou .png
- Os nomes dos arquivos podem ser encontrados em /storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/userdata/addon_data/plugin.video.pixel.canais/lista_de_canais.txt

<h2>Se quiser customizar o add-on</h2>

Para editar o addon é simples, ele é um zip, as imagens ficam em resources/media.

Para completar os que faltam é só olhar no log no pixel em /storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/userdata/addon_data/plugin.video.pixel.canais/pics_nao_encontradas.txt

As imagens tem que ser de tamanho 220x132 e pode ser jpg ou png.

Se  alterar alguma imagem e ela nao atualizar, as vezes tem que apagar a pasta /storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/userdata/Thumbnails pro kodi carregar novamente.

No arquivo canaisnet.txt contém os nomes dos canais que serão ocultos na opção "Ocultar canais informativos NET".

<h2>Bugs conhecidos</h2>

Quando é escolhido para ocultar canais, os canais ocultos ficam no topo da lista se estiver selecionado o grupo de canais DVB-C. Esse grupo é selecionado automaticamente quando abre o Kodi.

A única forma de contornar isso é não ter nenhum grupo, somente o "Todos os Canais" que é padrão do Kodi.

Para fazer isso:

- Abrir menu principal > Sistema > TV > Geral
- Desmarcar a opção "Sincronize grupos de canais com backend(s)"
- Nessa mesma tela ir em "Administrar Grupo" e remover todos os grupos, menos o "Todos os Canais"

Não sei se isso causa algum outro problema no Kodi.
