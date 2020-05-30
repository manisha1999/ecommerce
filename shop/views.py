from django.shortcuts import render
from  django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from math import ceil
from .models import Product,Contact,Order,Orderupdate
import json
from paytm import Checksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5';
# Create your views here.
def index(request):
    products =Product.objects.all()
    print(products)

    allprods =[]
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod =Product.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod,range(1,nslides),nslides])
    #params = {'no_of_slides':nslides,'range':range(1,nslides),'product' : products}
    #allprods =[[products,range(1,nslides),nslides],
     #          [products,range(1,nslides),nslides]]
    params = {'allprods':allprods}
    return render(request,'shop/index.html',params)

def searchMatch(query,item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        if (len(prod)!=0):
            allprods.append([prod, range(1, nslides), nslides])
    # params = {'no_of_slides':nslides,'range':range(1,nslides),'product' : products}
    # allprods =[[products,range(1,nslides),nslides],
    #          [products,range(1,nslides),nslides]]
    params = {'allprods': allprods, "msg":""}
    print(len(allprods))
    if len(allprods)==0:
        params={'msg':"Please make sure to enter relevant search queryh"}
    return render(request, 'shop/index.html',params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    thank =False
    if request.method=='POST':

        name = request.POST.get('name','')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        print(name,email,phone,desc)
        contact=Contact(name=name,email=email,phone=phone,desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html',{'thank' : thank})

def tracker(request):
    if request.method=='POST':

        orderid = request.POST.get('orderid','')
        email = request.POST.get('email', '')
        try:
            order = Order.objects.filter(order_id=orderid,email=email)
            if(len(order)>0):
                update = Orderupdate.objects.filter(order_id=orderid)
                updates=[]
                for item in update:
                    updates.append({'text':item.update_desc,'time':item.timestamp})
                    response = json.dumps({"status":"success", "updates":updates,"itemsJson":order[0].items_json},default=str)
                return HttpResponse('{"status":"noitem"}')
            else:
                return HttpResponse('{"status":"error"}')
        except Exception as e:
            return HttpResponse('error')
    return render(request, 'shop/tracker.html')

def prodview(request,myid):
    product = Product.objects.filter(id=myid)

    return render(request, 'shop/prodview.html',{'product':product[0]})

def checkout(request):
    if request.method=='POST':
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name','')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '')+" "+request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order=Order(items_json=items_json,name=name,email=email,address=address,city=city, state=state,zip_code=zip_code,phone=phone,amount=amount)
        order.save()
        update = Orderupdate(orderid=orderid,update_desc="The order has been placed")
        update.save()
        thank = True
        id =order.orderid
        #return render(request,'shop/checkout.html',{'thank':thank ,'id':id})
        param_dict= {
            'MID':'WorldP64425807474247',
            'ORDER_ID':str(order.orderid),
            'TXN_AMOUNT':str(amount),
            'CUST_ID':'email',
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict,MERCHANT_KEY)
        return render(request,'shop/paytm.html',{'param_dict':param_dict})

    return render(request, 'shop/checkout.html')

@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i =='CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checcksum(response_dict,MERCHANT_KEY,checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request,'shop/paymentstatus.html',{'response':response_dict})
