# Projeto - Computação em Nuvem - Insper 2024.2

Desenvolvedores: Carlos Eduardo Porciuncula Yamada

## Deploy GitHub Pages com MkDocs

A página contendo a documentação do projeto foi feita utilizando MkDocs junto a outras extensões como o Material for MkDocs e está disponível no GitHub Pages desse repositório.

Para desenvolvimento local, execute o comando, dentro da pasta `documentation`:

```bash
mkdocs serve
```

E acesse `http://localhost:8000.`

O deploy da aplicação foi feito utilizando o comando:

```bash
mkdocs gh-deploy --force
```

## Links

- [Docker Hub da aplicação](https://hub.docker.com/r/carlosepy/projeto-cloud)
- [Vídeo explicativo da aplicação](https://youtu.be/lr6lK1BI74w)
- [Link para a página da documentação da API](http://a09ee328db3f24b1fb7ce3264a54eb04-8417921.us-east-1.elb.amazonaws.com:8000/docs)
- [Vídeo sobre deployment da aplicação na AWS com EKS](https://youtu.be/q4yMWgXOMZU)
