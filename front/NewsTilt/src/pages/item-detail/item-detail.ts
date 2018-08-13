import { Component } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { Api } from '../../providers';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/fromPromise';

@IonicPage()
@Component({
  selector: 'page-item-detail',
  templateUrl: 'item-detail.html'
})
export class ItemDetailPage {
  article: any;

  constructor(public navCtrl: NavController, 
              navParams: NavParams,
              public sanitizer: DomSanitizer,
              public api: Api) {
    this.article = navParams.get('article');
    this.api.get('view/'+this.article.id).subscribe(O => {
      O.subscribe(resp => {
        console.log("DONE");
        console.log(resp);
      }, err => {
        console.error(err);
      })
    })
  }

  get_url(){
      return this.sanitizer.bypassSecurityTrustResourceUrl(this.article.url)
  }
  like(){
    console.log("LIKED!");
    this.api.get('like/'+this.article.id).subscribe(O => {
      O.subscribe(resp => {
        console.log("DONE");
        console.log(resp);
      }, err => {
        console.error(err);
      })
    })
  }
  swipe_left(){
      this.api.get('swipe/'+this.article.id+'/l').subscribe(O => {
      O.subscribe(resp => {
        console.log("DONE");
        console.log(resp);
      }, err => {
        console.error(err);
      })
    });
  }
  swipe_right(){
      this.api.get('swipe/'+this.article.id+'/r').subscribe(O => {
      O.subscribe(resp => {
        console.log("DONE");
        console.log(resp);
      }, err => {
        console.error(err);
      })
    });
  }
}
