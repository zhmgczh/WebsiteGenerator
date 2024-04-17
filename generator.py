import os,csv,hashlib,pickle,json
from bs4 import BeautifulSoup
hash_value=hashlib.new('sha256')
content_database={}
category_database={}
def load_content_database():
    global content_database,category_database
    if os.path.isfile('content_database.pkl'):
        with open('content_database.pkl','rb') as inp:
            content_database=pickle.load(inp)
def write_content_database(website_directory:str):
    global content_database,category_database
    with open('content_database.pkl',mode='wb') as outp:
        pickle.dump(content_database,outp,pickle.HIGHEST_PROTOCOL)
    original_directory=os.getcwd()
    os.chdir(website_directory)
    with open('./content_database.js',mode='w',encoding='utf-8') as js:
        json.dump(content_database,js)
    with open('./category_database.js',mode='w',encoding='utf-8') as js:
        json.dump(category_database,js)
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
def make_directory(name:str):
    if not os.path.isdir(name):
        os.makedirs(name)
def replace_tag(article:str,tag:str,replacement:str):
    return article.replace(tag,replacement)
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
def truncate(title:str):
    global filename_length_limit
    if len(title)>filename_length_limit:
        title=title[:-filename_length_limit]
    return title
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
            article=replace_tag(article,'<!--|||||description|||||-->',row[excerpt_index])
            article=replace_tag(article,'<!--|||||article_category|||||-->',row[category_index])
            article=replace_tag(article,'<!--|||||article_title|||||-->',row[title_index])
            article=replace_tag(article,'<!--|||||article_post|||||-->',row[content_index])
            article=replace_all_components(article)
            title=truncate(row[title_index])
            url='/'+title+'/'
            hash_value.update(article.encode())
            if url not in content_database or content_database[url]!=hash_value.hexdigest():
                make_directory(title)
                with open('./'+title+'/index.html',mode='w',encoding='utf-8') as file:
                    file.write(article)
                content_database[url]={'type':'article',
                                       'category':row[category_index],
                                       'title':row[title_index],
                                       'description':row[excerpt_index],
                                       'hash_value':hash_value.hexdigest()}
            if row[category_index] not in category_database:
                category_database[row[category_index]]=[]
            category_database[row[category_index]].append({'url':url,
                                                           'title':row[title_index],
                                                           'description':row[excerpt_index]})
    os.chdir(original_directory)
def generate_articles(directory:str,website_directory:str):
    global content_database
    with open('./article.html',mode='r',encoding='utf-8') as file:
        article_template=file.read()
    categories=os.listdir(directory)
    original_directory=os.getcwd()
    os.chdir(website_directory)
    for category in categories:
        if '.'!=category[0]:
            make_directory(category)
            os.chdir(category)
            articles=os.listdir(os.path.join(original_directory,directory,category))
            for article in articles:
                if article.endswith('.html'):
                    with open(os.path.join(original_directory,directory,category,article),mode='r',encoding='utf-8') as file:
                        post_content=file.read()
                        cleantext=BeautifulSoup(post_content,'lxml').text.replace('\n\n','\n')
                        title=article[:-len('.html')]
                        post=article_template
                        post=replace_tag(post,'<!--|||||description|||||-->',cleantext)
                        post=replace_tag(post,'<!--|||||article_category|||||-->',category)
                        post=replace_tag(post,'<!--|||||article_title|||||-->',title)
                        post=replace_tag(post,'<!--|||||article_post|||||-->',post_content)
                        post=replace_all_components(post)
                        truncated_title=truncate(title)
                        url='/'+truncated_title+'/'
                        hash_value.update(post.encode())
                        if url not in content_database or content_database[url]!=hash_value.hexdigest():
                            make_directory(truncated_title)
                            with open('./'+truncated_title+'/index.html',mode='w',encoding='utf-8') as file:
                                file.write(post)
                            content_database[url]={'type':'article',
                                                   'category':category,
                                                   'title':title,
                                                   'description':cleantext,
                                                   'hash_value':hash_value.hexdigest()}
                        if category not in category_database:
                            category_database[category]=[]
                        category_database[category].append({'url':url,
                                                            'title':title,
                                                            'description':cleantext})
            os.chdir('..')
    os.chdir(original_directory)
def generate_categories(website_directory:str):
    pass
def generate_pages(directory:str,website_directory:str):
    pass
def generate_sitemap(website_directory:str):
    pass
def main(website_directory:str='./NTCCTMCR/',
         entries_filepath:str='../import.csv',
         articles_directory:str='../WordPress/articles',
         pages_directory:str='../WordPress/pages',
         domain_name_str:str='www.zh-tw.top',
         base_url_str:str='https://www.zh-tw.top',
         filename_length_limit_str:int=22):
    global domain_name,base_url,filename_length_limit
    domain_name=domain_name_str
    base_url=base_url_str
    filename_length_limit=int(filename_length_limit_str)
    original_directory=os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    load_component_map()
    load_content_database()
    generate_entries(entries_filepath,website_directory)
    generate_articles(articles_directory,website_directory)
    generate_categories(website_directory)
    generate_pages(pages_directory,website_directory)
    generate_sitemap(website_directory)
    write_content_database(website_directory)
    os.chdir(original_directory)
if '__main__'==__name__:
    import sys
    if 8==len(sys.argv):
        main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],int(sys.argv[7]))
    else:
        main()