import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { IonicPage, NavController, ToastController } from 'ionic-angular';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/observable/fromPromise'
import { User, Settings } from '../../providers';
import { MainPage } from '../';

@IonicPage()
@Component({
  selector: 'page-login',
  templateUrl: 'login.html'
})
export class LoginPage {
  // The account fields for the login form.
  // If you're using the username field with or without email, make
  // sure to add it to the type
  account: { username: string, password: string } = {
    username: '',
    password: ''
  };

  // Our translated text strings
  private loginErrorString: string;

  constructor(public navCtrl: NavController,
    public user: User,
    public toastCtrl: ToastController,
    public translateService: TranslateService,
    public settings: Settings) {

    this.translateService.get('LOGIN_ERROR').subscribe((value) => {
      this.loginErrorString = value;
    })

    Observable.fromPromise(this.settings.getValue('user')).subscribe((value:any) =>{
      if (value != null){
        this.navCtrl.push(MainPage);      
      }      
    }, (err) => {
    });
  }

  // Attempt to login in through our User service
  doLogin() {
    console.log(this.account.password)
    this.user.login(this.account).subscribe(O => {
      O.subscribe((resp) => {
        this.navCtrl.push(MainPage);
        let toast = this.toastCtrl.create({
          message: "Welcome to NewsTilt",
          duration: 3000,
          position: 'top'
        });
        toast.present();
      })
    }, (err) => {
      // this.navCtrl.push(MainPage);
      // Unable to log in
      console.log(err)
      let toast = this.toastCtrl.create({
        message: this.loginErrorString,
        duration: 3000,
        position: 'top'
      });
      toast.present();
    });
  }
}
