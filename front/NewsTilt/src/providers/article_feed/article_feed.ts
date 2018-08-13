import { Injectable } from '@angular/core';
import { Api } from '../';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/toPromise';

@Injectable()
export class ArticleFeed {
    constructor(public api: Api) { }
    

    query(start_idx,feed_len) {
        let req = this.api.get('feed/'+start_idx+'/'+feed_len);
        return req;
    }
}
