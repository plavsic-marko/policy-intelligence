from scripts.weaviate_client import WVT


def main():
    query = """
    {
      Get {
        IETF_ArticleChunks(
          limit: 3
        ) {
          title
          author
          url
          quarter
          text
        }
      }
    }
    """

    result = WVT.query.raw(query)
    print(result)


if __name__ == "__main__":
    main()
