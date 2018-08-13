import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { Settings } from '../settings/settings'
import 'rxjs/add/observable/fromPromise'

/**
 * Api is a generic REST Api handler. Set your API url first.
 */
@Injectable()
export class Api {
  url: string = 'https://news-tilt-backend.herokuapp.com';
  auth_info: {username: string, password: string} = null;

  createAuthorizationHeader(auth_info: {username: string, password: string},
                            headers: HttpHeaders) {
    headers.set('Authorization', 'Basic ' +
      btoa(auth_info.username +':'+ auth_info.password)); 
  }

  constructor(public http: HttpClient,
              public settings: Settings) {
  }


  get(endpoint: string, params?: any, reqOpts?: any) {
    console.log(this.auth_info)
    if (!reqOpts) {
      reqOpts = {
        params: new HttpParams()
      };
    }

    // Support easy query params for GET requests
    if (params) {
      reqOpts.params = new HttpParams();
      for (let k in params) {
        reqOpts.params = reqOpts.params.set(k, params[k]);
      }
    }

    let req = this.settings.getValue('user').then((value:any) =>{
      if (value != null){
        console.log(value);
        let headers = new HttpHeaders();
        headers = headers.set('Authorization', 'Basic ' + value)
        return this.http.get(this.url + '/' + endpoint, {headers: headers});
      }
      else{
        return this.http.get(this.url + '/' + endpoint);
      }
    })        
    return Observable.fromPromise(req)
  }

  post(endpoint: string, body: any, reqOpts?: any) {
    let req = this.settings.getValue('user').then((value:any) =>{
      if (value != null){
        console.log(value);
        let headers = new HttpHeaders();
        headers = headers.set('Authorization', 'Basic ' + value)
        return this.http.post(this.url + '/' + endpoint, body, {headers: headers});
      }
      else{
        return this.http.post(this.url + '/' + endpoint, body);
      }
    })    
    return Observable.fromPromise(req)        
  }

  put(endpoint: string, body: any, reqOpts?: any) {
    return this.http.put(this.url + '/' + endpoint, body, reqOpts);
  }

  delete(endpoint: string, reqOpts?: any) {
    return this.http.delete(this.url + '/' + endpoint, reqOpts);
  }

  patch(endpoint: string, body: any, reqOpts?: any) {
    return this.http.patch(this.url + '/' + endpoint, body, reqOpts);
  }

  set_auth_info(info){
    this.auth_info = info;
  }
}
