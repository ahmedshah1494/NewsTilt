import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { IonicPage, NavController, ToastController } from 'ionic-angular';
import { Observable } from 'rxjs/Observable';
import { User, Api } from '../../providers';
import { LoginPage } from '../';

@IonicPage()
@Component({
  selector: 'page-signup',
  templateUrl: 'signup.html'
})
export class SignupPage {
  // The account fields for the login form.
  // If you're using the username field with or without email, make
  // sure to add it to the type
  account: { first_name: string, last_name: string, username: string, password: string, categories: any[] } = {
    first_name: '',
    last_name: '',
    username: '',
    password: '',
    categories: []
  };

  categories = [];
  // Our translated text strings
  private signupErrorString: string;

  constructor(public navCtrl: NavController,
    public user: User,
    public api: Api,
    public toastCtrl: ToastController,
    public translateService: TranslateService) {

    this.translateService.get('SIGNUP_ERROR').subscribe((value) => {
      this.signupErrorString = value;
    })
    this.populateCategories();
  }

  populateCategories() {
    let req = this.api.get('get_categories').share()
    req.subscribe(O => {
      O.subscribe((res:any) => {
        for (var i = res.length - 1; i >= 0; i--) {          
          this.categories.push({id: res[i].id, name: res[i].name, ischecked: false})
        }
      })
    })
  }

  doSignup() {
    // Attempt to login in through our User service
    this.account.categories = [];
    this.categories.forEach(cat =>{
      if (cat.ischecked){
        this.account.categories.push({id: cat.id, name: cat.name})
      }      
    })
    this.user.signup(this.account).subscribe(O => {
        O.subscribe((resp) => {
          let toast = this.toastCtrl.create({
            message: "An activation email has been sent to "+this.account.username,
            duration: 5000,
            position: 'top'
          });
          toast.present();
          this.navCtrl.push(LoginPage);      
        }, (err) => {

          // this.navCtrl.push(MainPage);

          // Unable to sign up
          let toast = this.toastCtrl.create({
            message: this.signupErrorString,
            duration: 3000,
            position: 'top'
        });
        toast.present();
      });
    })
  }
}
