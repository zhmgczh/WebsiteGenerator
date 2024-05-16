import os,csv,hashlib,pickle,json
from bs4 import BeautifulSoup
from urllib.parse import quote
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
                    with open(os.path.join('./components/',row[file_index]),mode='r',encoding='utf-8') as file:
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
            article=replace_tag(article,component,component_map[component])
        if article_backup==article:
            break
    return article
def remove_double_newline_and_truncate(article:str):
    while -1!=article.find('\n\n'):
        article=article.replace('\n\n','\n')
    while -1!=article.find('\n '):
        article=article.replace('\n ','\n')
    while -1!=article.find(' \n'):
        article=article.replace(' \n','\n')
    while -1!=article.find('  '):
        article=article.replace('  ',' ')
    return article.strip()
def truncate(title:str):
    global filename_length_limit
    if len(title)>filename_length_limit:
        title=title[:filename_length_limit]
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
            cleantext=remove_double_newline_and_truncate(BeautifulSoup(row[content_index],'lxml').text)
            article=article_template
            article=replace_all_components(article)
            # article=replace_tag(article,'<!--|||||description|||||-->',row[excerpt_index])
            article=replace_tag(article,'<!--|||||description|||||-->',cleantext)
            article=replace_tag(article,'<!--|||||article_category|||||-->',row[category_index])
            article=replace_tag(article,'<!--|||||article_category_encoded|||||-->',quote(row[category_index]))
            article=replace_tag(article,'<!--|||||article_title|||||-->',row[title_index])
            article=replace_tag(article,'<!--|||||article_post|||||-->',row[content_index])
            title=truncate(row[title_index])
            url=replace_all_components(quote(os.path.join('/',row[category_index],title)+'/').replace('//','/').lower())
            article=replace_tag(article,'<!--|||||link_url|||||-->',url)
            article=replace_tag(article,'<!--|||||full_url|||||-->',base_url+url)
            article=replace_all_components(article)
            hash_value.update(article.encode())
            if url not in content_database or content_database[url]['hash_value']!=hash_value.hexdigest():
                make_directory(title)
                with open(os.path.join('./',title,'index.html'),mode='w',encoding='utf-8') as file:
                    file.write(article)
                content_database[url]={'type':'article',
                                       'category':row[category_index],
                                       'title':row[title_index],
                                       'description':cleantext,
                                    #    'description':row[excerpt_index],
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
                        cleantext=remove_double_newline_and_truncate(BeautifulSoup(post_content,'lxml').text)
                        title=article[:-len('.html')]
                        post=article_template
                        post=replace_all_components(post)
                        post=replace_tag(post,'<!--|||||description|||||-->',cleantext)
                        post=replace_tag(post,'<!--|||||article_category|||||-->',category)
                        post=replace_tag(post,'<!--|||||article_category_encoded|||||-->',quote(category))
                        post=replace_tag(post,'<!--|||||article_title|||||-->',title)
                        post=replace_tag(post,'<!--|||||article_post|||||-->',post_content)
                        truncated_title=truncate(title)
                        url=replace_all_components(quote(os.path.join('/',category,truncated_title)+'/').replace('//','/').lower())
                        post=replace_tag(post,'<!--|||||link_url|||||-->',url)
                        post=replace_tag(post,'<!--|||||full_url|||||-->',base_url+url)
                        post=replace_all_components(post)
                        hash_value.update(post.encode())
                        if url not in content_database or content_database[url]['hash_value']!=hash_value.hexdigest():
                            make_directory(truncated_title)
                            with open(os.path.join('./',truncated_title,'index.html'),mode='w',encoding='utf-8') as file:
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
def generate_pages(directory:str,website_directory:str):
    global content_database
    original_directory=os.getcwd()
    with open(os.path.join(original_directory,directory,'alias.csv'),mode='r',encoding='utf-8') as csv_file:
        csv_reader=csv.reader(csv_file)
        alias={}
        title_index=alias_index=-1
        for row in csv_reader:
            if -1 in(title_index,alias_index):
                title_index=row.index('page_title')
                alias_index=row.index('alias')
            else:
                alias[row[title_index]]=row[alias_index]
    with open(os.path.join(original_directory,directory,'page_components.csv'),mode='r',encoding='utf-8') as csv_file:
        csv_reader=csv.reader(csv_file)
        page_components={}
        father_index=tag_index=child_index=-1
        for row in csv_reader:
            if -1 in(father_index,tag_index,child_index):
                father_index=row.index('father')
                tag_index=row.index('tag')
                child_index=row.index('child')
            else:
                if row[father_index] not in page_components:
                    page_components[row[father_index]]={}
                with open(os.path.join(original_directory,directory,row[child_index]),mode='r',encoding='utf-8') as file:
                    page_components[row[father_index]][row[tag_index]]=file.read()
    with open('./page.html',mode='r',encoding='utf-8') as file:
        page_template=file.read()
    os.chdir(website_directory)
    pages=os.listdir(os.path.join(original_directory,directory))
    for page in pages:
        if page.endswith('.html'):
            with open(os.path.join(original_directory,directory,page),mode='r',encoding='utf-8') as file:
                post_content=file.read()
                cleantext=remove_double_newline_and_truncate(BeautifulSoup(post_content,'lxml').text)
                title=page[:-len('.html')]
                post=page_template
                post=replace_all_components(post)
                post=replace_tag(post,'<!--|||||description|||||-->',cleantext)
                post=replace_tag(post,'<!--|||||page_title|||||-->',title)
                post=replace_tag(post,'<!--|||||page_post|||||-->',post_content)
                post=replace_all_components(post)
                if title in alias:
                    if 'index'==alias[title]:
                        truncated_title=''
                    else:
                        truncated_title=alias[title]#truncate(alias[title])
                else:
                    truncated_title=title#truncate(title)
                if page in page_components:
                    for tag in page_components[page]:
                        post=replace_tag(post,tag,page_components[page][tag])
                url=replace_all_components(quote(os.path.join('/',truncated_title)+'/').replace('//','/').lower())
                post=replace_tag(post,'<!--|||||link_url|||||-->',url)
                post=replace_tag(post,'<!--|||||full_url|||||-->',base_url+url)
                hash_value.update(post.encode())
                if url not in content_database or content_database[url]['hash_value']!=hash_value.hexdigest():
                    if ''!=truncated_title:
                        make_directory(truncated_title)
                    with open(os.path.join('./',truncated_title,'index.html'),mode='w',encoding='utf-8') as file:
                        file.write(post)
                    content_database[url]={'type':'page',
                                           'title':title,
                                           'description':cleantext,
                                           'hash_value':hash_value.hexdigest()}
    os.chdir(original_directory)
def generate_categories(website_directory:str):
    global category_database
    original_directory=os.getcwd()
    with open('./category.html',mode='r',encoding='utf-8') as file:
        category_template=file.read()
    os.chdir(website_directory)
    make_directory('category')
    os.chdir('category')
    for category in category_database:
        post=category_template
        post=replace_all_components(post)
        post=replace_tag(post,'<!--|||||category|||||-->',category)
        post=replace_tag(post,'<!--|||||description|||||-->','「'+category+'」系列所有文章列表 - 大陸居民臺灣正體字講義')
        url=replace_all_components(quote(os.path.join('/category/',category)+'/').replace('//','/').lower())
        post=replace_tag(post,'<!--|||||link_url|||||-->',url)
        post=replace_tag(post,'<!--|||||full_url|||||-->',base_url+url)
        post=replace_tag(post,'<!--|||||next_url|||||-->',url+'?page=2')
        post=replace_all_components(post)
        hash_value.update(post.encode())
        if url not in content_database or content_database[url]['hash_value']!=hash_value.hexdigest():
            make_directory(category)
            with open(os.path.join('./',category,'index.html'),mode='w',encoding='utf-8') as file:
                file.write(post)
            content_database[url]={'type':'category',
                                   'title':category,
                                   'description':'「'+category+'」系列所有文章列表 - 大陸居民臺灣正體字講義',
                                   'hash_value':hash_value.hexdigest()}
    os.chdir(original_directory)
def generate_search(website_directory:str):
    original_directory=os.getcwd()
    with open('./search.html',mode='r',encoding='utf-8') as file:
        search_template=file.read()
    os.chdir(website_directory)
    make_directory('search')
    os.chdir('search')
    post=search_template
    post=replace_all_components(post)
    post=replace_tag(post,'<!--|||||description|||||-->','搜索 - 大陸居民臺灣正體字講義')
    url='/search/'
    post=replace_tag(post,'<!--|||||link_url|||||-->',url)
    post=replace_tag(post,'<!--|||||full_url|||||-->',base_url+url)
    post=replace_tag(post,'<!--|||||next_url|||||-->',url+'?page=2')
    post=replace_all_components(post)
    hash_value.update(post.encode())
    if url not in content_database or content_database[url]['hash_value']!=hash_value.hexdigest():
        with open(os.path.join('./index.html'),mode='w',encoding='utf-8') as file:
            file.write(post)
        content_database[url]={'type':'search',
                               'title':'搜索 - 大陸居民臺灣正體字講義',
                               'description':'搜索 - 大陸居民臺灣正體字講義',
                               'hash_value':hash_value.hexdigest()}
    os.chdir(original_directory)
def generate_404(website_directory:str):
    original_directory=os.getcwd()
    with open('./404.html',mode='r',encoding='utf-8') as file:
        template_404=file.read()
    os.chdir(website_directory)
    post=template_404
    post=replace_all_components(post)
    post=replace_tag(post,'<!--|||||description|||||-->','找不到符合條件的頁面 – 大陸居民臺灣正體字講義')
    url='/404.html'
    post=replace_tag(post,'<!--|||||link_url|||||-->',url)
    post=replace_tag(post,'<!--|||||full_url|||||-->',base_url+url)
    post=replace_tag(post,'<!--|||||next_url|||||-->',url+'?page=2')
    hash_value.update(post.encode())
    if url not in content_database or content_database[url]['hash_value']!=hash_value.hexdigest():
        with open(os.path.join('./404.html'),mode='w',encoding='utf-8') as file:
            file.write(post)
        content_database[url]={'type':'404',
                               'title':'找不到符合條件的頁面 – 大陸居民臺灣正體字講義',
                               'description':'找不到符合條件的頁面 – 大陸居民臺灣正體字講義',
                               'hash_value':hash_value.hexdigest()}
    os.chdir(original_directory)
def generate_sitemap(website_directory:str):
    global content_database
    original_directory=os.getcwd()
    urls=[base_url+url for url in content_database.keys()]
    xml_data="""<?xml version='1.0' encoding='UTF-8'?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""
    for url in urls:
        xml_data+='<url><loc>'+url+'</loc></url>'
    xml_data+='</urlset>'
    os.chdir(website_directory)
    with open('./sitemap.xml',mode='w',encoding='utf-8') as file:
        file.write(xml_data)
    os.chdir(original_directory)
def main(website_directory:str='./NTCCTMCR/',
         entries_filepath:str='../import.csv',
         articles_directory:str='../WordPress/articles',
         pages_directory:str='../WordPress/pages',
         base_url_str:str='https://static.zh-tw.top',
         filename_length_limit_str:int=22):
    global base_url,filename_length_limit
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
    generate_search(website_directory)
    generate_404(website_directory)
    generate_sitemap(website_directory)
    write_content_database(website_directory)
    os.chdir(original_directory)
if '__main__'==__name__:
    import sys
    if 8==len(sys.argv):
        main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],int(sys.argv[7]))
    else:
        main()