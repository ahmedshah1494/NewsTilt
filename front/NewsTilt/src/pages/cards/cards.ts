import { Component } from '@angular/core';
import { IonicPage, NavController } from 'ionic-angular';
import { ArticleFeed, User } from '../../providers';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/fromPromise';
import { LoginPage } from '../';
import { ArticlePage } from '../';

@IonicPage()
@Component({
  selector: 'page-cards',
  templateUrl: 'cards.html'
})

export class CardsPage {
  cardItems = [];
  neutral_margin = 0.2;
  slight_margin = 0.5;
  extreme_margin = 0.8;
  start_idx = 0
  feed_len = 10
  constructor(public navCtrl: NavController,
              public feed: ArticleFeed,
              public user: User) {
    
    feed.query(this.start_idx,this.feed_len).subscribe(O => {
      O.subscribe((value:any) => {
        this.update_feed(value);
      })
    })
    
  }

  update_feed(value:any){
    this.start_idx = this.start_idx + value.length;    
    value.forEach(item => {
      let tilt = item.tilt;
      item.tilt = [item.tilt,""]
      if (Math.abs(tilt) < this.neutral_margin){
        item.tilt[1] = "Neutral";            
      }
      else {
        if (Math.abs(tilt) < this.slight_margin){
        item.tilt[1] = "Slightly "
        }
        else if (Math.abs(tilt) > this.extreme_margin){
          item.tilt[1] = "Extremely "
        };
        if (tilt < 0){
          item.tilt[1] = item.tilt[1] + "Left";
        }
        if (tilt > 0){
          item.tilt[1] = item.tilt[1] + "Right";
        }
      }
      this.cardItems.push(item);
    })
    console.log('card_list')
    console.log(this.cardItems)
  }

  open_article(article){
    this.navCtrl.push(ArticlePage, {article: article});
  }

  logout(){
    this.user.logout().then(val=>{
      this.navCtrl.push(LoginPage);
    })    
  }

  doInfinite(): Promise<any> {
    console.log('Begin async operation');
    let req = this.feed.query(this.start_idx, this.feed_len).toPromise();
    req.then(O => {
      O.subscribe(res => {
        console.log(res)
        this.update_feed(res);
      })
      
    })
    return req;
  }  
}
