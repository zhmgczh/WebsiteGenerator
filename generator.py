import os,csv,hashlib,pickle,json
hash_value=hashlib.new('sha256')
content_database={}
def load_content_database():
    global content_database
    if os.path.isfile('content_database.pkl'):
        with open('content_database.pkl','rb') as inp:
            content_database=pickle.load(inp)
def write_content_database(website_directory:str):
    global content_database
    with open('content_database.pkl',mode='wb') as outp:
        pickle.dump(content_database,outp,pickle.HIGHEST_PROTOCOL)
    original_directory=os.getcwd()
    os.chdir(website_directory)
    with open('./content_database.js',mode='w',encoding='utf-8') as js:
        json.dump(content_database,js)
    os.chdir(original_directory)
component_map={}
def load_component_map():
    global component_map
    with open('./component.csv',mode='r',encoding='utf-8') as csv_file:
        csv_reader=csv.reader(csv_file)
        id_index=file_index=-1
        for row in csv_reader:
            if -1 in(id_index,file_index):
                id_index=row.index('component_id')
                file_index=row.index('component_file')
            else:
                if ''!=row[file_index]:
                    with open('./components/'+row[file_index],mode='r',encoding='utf-8') as file:
                        component_map[row[id_index]]=file.read()
def make_directory(address:str):
    if not os.path.isdir(address):
        os.makedirs(address)
def replace_tag(article:str,tag:str,replacement:str):
    return article.replace('<!--|||||'+tag+'|||||-->',replacement)
def replace_all_components(article:str):
    global component_map
    while True:
        article_backup=article
        for component in component_map:
            if ''!=component_map[component]:
                article=replace_tag(article,component,component_map[component])
        if article_backup==article:
            break
    return article
def generate_entries(filepath:str,website_directory:str):
    global content_database
    with open('./article.html',mode='r',encoding='utf-8') as file:
        article_template=file.read()
    rows=[]
    with open(filepath,mode='r',encoding='utf-8') as csv_file:
        csv_reader=csv.reader(csv_file)
        for row in csv_reader:
            rows.append(row)
    original_directory=os.getcwd()
    os.chdir(website_directory)
    make_directory('一簡多繁辨析')
    os.chdir('./一簡多繁辨析')
    title_index=content_index=excerpt_index=category_index=-1
    for row in rows:
        if -1 in (title_index,content_index,excerpt_index,category_index):
            title_index=row.index('title')
            content_index=row.index('content')
            excerpt_index=row.index('excerpt')
            category_index=row.index('category')
        else:
            article=article_template
            article=replace_tag(article,'description',row[excerpt_index])
            article=replace_tag(article,'article_category',row[category_index])
            article=replace_tag(article,'article_title',row[title_index])
            article=replace_tag(article,'article_post',row[content_index])
            article=replace_all_components(article)
            url='/'+row[title_index]+'/'
            hash_value.update(article.encode())
            if url not in content_database or content_database[url]!=hash_value.hexdigest():
                make_directory(row[title_index])
                with open('./'+row[title_index]+'/index.html',mode='w',encoding='utf-8') as file:
                    file.write(article)
                content_database[url]={'type':'article',
                                       'category':row[category_index],
                                       'title':row[title_index],
                                       'description':row[excerpt_index],
                                       'hash_value':hash_value.hexdigest()}
    os.chdir(original_directory)
def generate_articles(directory:str,website_directory:str):
    pass
def generate_categories(website_directory:str):
    pass
def generate_pages(directory:str,website_directory:str):
    pass
def generate_sitemap(website_directory:str):
    pass
def main(website_directory:str='./NTCCTMCR/',entries_filepath:str='../import.csv',articles_directory:str='../WordPress/articles',pages_directory:str='../WordPress/pages'):
    load_component_map()
    load_content_database()
    generate_entries(entries_filepath,website_directory)
    generate_articles(articles_directory,website_directory)
    generate_categories(website_directory)
    generate_pages(pages_directory,website_directory)
    generate_sitemap(website_directory)
    write_content_database(website_directory)
if '__main__'==__name__:
    import sys
    if 6==len(sys.argv):
        main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
    else:
        main()