/*
 * This file is part of Anicat.
 *
 * Anicat is distributed under the terms of Anicat License.
 * See <http://www.anicat.net/LICENSE/> for feature details.
 *
 * Card module
 *
 */


var Card = new (function(){

    var processor = new RequestProcessor({'card': function(resp){
                message.hide();
                Card.create(resp.id, resp.text);
        }});

    this.init = function(){
        Card.load();
    }

    this.load = function(){
        var card = document.getElementById('card') || document.getElementById('pagecard');
        if(!isOldIE)
            this.hideEdits(card);
        if(!card || !card.clientWidth) return;
        var imgbun;
        if(card.clientWidth < 750){
            imgbun = (card.clientWidth < 600) ? 200 : 300;
            card.firstChild.style.maxWidth = imgbun + 'px';
            card.firstChild.firstChild.firstChild.style.maxWidth = imgbun + 'px';
            imgbun += 40;
        }else{
            imgbun = card.firstChild.clientWidth + 40;
        }
        card.lastChild.previousSibling.style.maxWidth = card.clientWidth - imgbun - 20 + 'px';
    }

    this.hideEdits = function(p){
        if(!p) return;
        var h = new Array();
        var c = getElementsByClassName('right', p);
        for(var i=0; i<c.length; i++){
            if(!c[i] || c[i].tagName != "A") continue;
            h.push(c[i]);
        }
        if(!h.length) return;
        for(var element=0; element<h.length; element++){
            var c = h[element];
            toggle(c, -1);
            addEvent(c.parentNode, 'mouseover', edit.showEdit);
            addEvent(c.parentNode, 'mouseout', edit.hideEdit);
        }
    }

    this.create = function(id, res){
        if(!id || !res)
            throw new Error('Bad data passed for card creration');
        var card = document.getElementById("card");
        var data = new Array();
        var fields = ['name', 'type', 'genre', 'episodesCount',
                    'duration', 'release', 'links', 'state']
        for(var i=0; i<fields.length; i++){
            data.push(forms.getTitledField(fields[i], id, res[fields[i]]));
        }
        var bundle = forms.getTitledField('bundle', id, res.bundle)
        var link = null;
        if(isArray(bundle)){
            link = bundle.pop();
            bundle = bundle.pop()
        }
        element.appendChild(card, [
            {'div': {'id': 'imagebun', 'className': 'cardcol'}}, [
                {'div': {'id': 'cimg'}}, [
                    {'img': {'src': 'http://anicat.net/images/' + res.id + '/'}},
                    forms.getEditLink('image', id, 'Submit new'),
                    forms.getField('image', res.id)],
                link, bundle
            ],
            {'div': {'id': 'main', 'className': 'cardcol'}}, data,
            {'div': {'className': 'left'}}, [
                {'a': {'innerText': '✕', 'onclick': this.close}},
                {'a': {'innerText': '↪', 'href': '/card/' + id + '/', target: '_blank'}},
            ]

        ]);
        this.place(true);
        this.load();
    }

    this.close = function(){
        toggle(document.getElementById("card"), -1);
    }

    this.get = function(id, e){
        var card = document.getElementById("card");
        if(card){
            var tbl = document.getElementById("tbl");
            var w = document.documentElement.clientWidth - tbl.clientWidth - 70;
            element.removeAllChilds(card);
            card.style.width = w + 'px';
            if(w >= 500){
                if(e) message.toEventPosition(e);
                ajax.load('get', {'id': id, 'card': true, 'field': [
                    'id', 'bundle', 'name', 'type', 'genre', 'episodesCount',
                    'duration', 'release', 'links', 'state']}, processor);
                return false;
            }
        }
        return true;
    }

    this.place = function(show){
        var card = document.getElementById("card");
        if(!card) return;
        if(show) toggle(card, true);
        var soffsety = (document.documentElement.scrollTop || document.body.scrollTop) - document.documentElement.clientTop;
        var scry = 0;
        if(isNumber(window.pageYOffset))
            scry = window.pageYOffset;
        else if(document.body && document.body.scrollTop)
            scry = document.body.scrollTop;
        else if(document.documentElement && document.documentElement.scrollTop)
            scry = document.documentElement.scrollTop;
        if(!user.logined){
            var l = document.getElementById('loginform');
            if(visible(l) && soffsety < l.scrollHeight)
                soffsety = l.scrollHeight + 30 - (scry ? 0 : 40);
        }
        card.style.top = soffsety + (scry ? 5 : 40) + 'px';
    }

})();

addEvent(window, 'load', Card.init);
