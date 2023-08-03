from django.shortcuts import render,redirect
from shop.models import Product
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from cart.models import Cart,Account,Order
@login_required()
def cartview(request):
    total=0
    user=request.user
    try:
        cart=Cart.objects.filter(user=user)
        for i in cart:
            total+=i.quantity*i.product.price
    except Cart.DoesNotExist:
        pass
    return render(request,'cartview.html',{'cart':cart,'total':total})
@login_required()
def add_to_cart(request,b):
    b=Product.objects.get(id=b)
    user=request.user
    try:
        cart=Cart.objects.get(user=user,product=b)
        if(cart.quantity<cart.product.stock):
            cart.quantity+=1
            cart.save()
    except Cart.DoesNotExist:
        cart=Cart.objects.create(user=user,product=b,quantity=1)
        cart.save()
    return redirect('cart:cartview')
@login_required()
def cart_remove(request,b):
    b=Product.objects.get(id=b)
    user=request.user
    try:
        cart=Cart.objects.get(user=user,product=b)
        if(cart.quantity>1):
            cart.quantity-=1
            cart.save()
        else:
            cart.delete()
    except Cart.DoesNotExist:
        pass
    return redirect('cart:cartview')
@login_required()
def cart_delete(request,b):
    b=Product.objects.get(id=b)
    user=request.user
    try:
        cart=Cart.objects.get(user=user,product=b)
        cart.delete()
    except Cart.DoesNotExist:
        pass
    return redirect('cart:cartview')
@login_required()
def orderform(request):
    total=0
    if(request.method=="POST"):
        a=request.POST['a']
        p=request.POST['p']
        n=request.POST['n']
        user=request.user
        cart=Cart.objects.filter(user=user)
        for i in cart:
            total+=i.quantity*i.product.price
            ac=Account.objects.get(acctnumber=n)
            if(ac.amount>=total):
                ac.amount=ac.amount-total
                ac.save()
                for i in cart:
                    o=Order.objects.create(user=user,product=i.product,address=a,phone=p,order_status="paid",noofitems=i.quantity)
                    o.save()
                    i.product.stock=i.product.stock-i.quantity
                    i.product.save()
                    cart.delete()
                    msg="order placed successfully"
                return render(request,'orderdetail.html',{'msg':msg})
            else:
                msg="insufficient amount,you cannot place order"
                return render(request,'orderdetail.html',{'msg':msg})
    return render(request,'orderform.html')
@login_required()
def orderview(request):
    user = request.user
    b=Order.objects.filter(user=user,order_status="paid")

    return render(request,'orderview.html',{'b':b,'user':user.username})