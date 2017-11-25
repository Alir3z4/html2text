[ ![The Baeldung logo](http://www.baeldung.com/wp-
content/themes/baeldung/icon/logo.svg) ](http://baeldung.com "Baeldung")

  * [![](http://www.baeldung.com/wp-content/themes/baeldung/icon/logo.svg)](http://www.baeldung.com "Baeldung")
  * [Start Here](/start-here)
  * [Courses ▼▲](javascript:void\(0\))

    * [

###  REST with Spring

The canonical reference for building a production grade API with Spring.

](/rest-with-spring-course "The “REST With Spring” Course")

    * [

###  Learn Spring Security

THE unique Spring Security education if you’re working with Java today.

](/learn-spring-security-course "The “Learn Spring Security” Course")

  * [Guides ▼▲](javascript:void\(0\))

    * [

###  Persistence

The main persistence with Spring guides here at Baeldung.

](/persistence-with-spring-series/ "Persistence with Spring")

    * [

###  REST

The main guides on REST APIs with Spring, here at Baeldung.

](/rest-with-spring-series/ "REST with Spring")

    * [

###  Security

The main Spring Security guides here at Baeldung.

](/security-spring "Security with Spring")

  * [About ▼▲](javascript:void\(0\))

    * [

###  Consulting

My consulting engagements

](/consulting)

    * [

###  Full Archive

The high level overview of all the articles on the site.

](http://www.baeldung.com/full_archive)

    * [

###  Write For Baeldung

Become a writer on the site.

](http://www.baeldung.com/contribution-guidelines)

    * [

###  About Baeldung

About Baeldung.

](http://www.baeldung.com/about/)

  * [](/feed)

# Intro to WebSockets with Spring

Last modified: July 19, 2017

by  [baeldung](http://www.baeldung.com/author/baeldung/ "Posts by baeldung")

  * [Spring](http://www.baeldung.com/category/spring/)+

### **The Price of all “Learn Spring Security” course packages will
permanently increase **by $50 on the 8th of December:****

**[>>> GET ACCESS NOW](/learn-spring-security-course#table)**

## **1\. Overview**

In this article, we will create a simple web application that implements
messaging using the **new WebSocket capabilities** introduced with Spring
Framework 4.0.

WebSockets are a **bi-directional** , **full-duplex** , **persistent
connection** between a web browser and a server. Once a WebSocket connection
is established the connection stays open until the client or server decides to
close this connection.

A typical use case could be when an app involves multiple users communicating
with each other, like in a chat. We will build a simple chat client in our
example.  

## **2\. Maven Dependencies**

Since this is a Maven-based project, we first add the required dependencies to
the _pom.xml_ :

    
    
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-websocket</artifactId>
        <version>4.2.4.RELEASE</version>
    </dependency>
    
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-messaging</artifactId>
        <version>4.2.4.RELEASE</version>
    </dependency>

In addition, as we'll use _JSON_ to build the body of our messages, we need to
add the _Jackson_ dependencies. This allows Spring to convert our Java object
to/from _JSON_ :

    
    
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-core</artifactId>
        <version>2.7.3</version>
    </dependency>
    
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId> 
        <version>2.7.3</version>
    </dependency>

If you want to get the newest version of the libraries above, look for them on
[Maven Central](http://search.maven.org/).

## **3\. Enable WebSocket in Spring**

The first thing to do is to enable the WebSocket capabilities. To do this we
need to add a configuration to our application and annotate this class with
_@EnableWebSocketMessageBroker_. As its name suggests, it enables WebSocket
message handling, backed by a message broker:

    
    
    @Configuration
    @EnableWebSocketMessageBroker
    public class WebSocketConfig extends AbstractWebSocketMessageBrokerConfigurer {
    
        @Override
        public void configureMessageBroker(MessageBrokerRegistry config) {
            config.enableSimpleBroker("/topic");
            config.setApplicationDestinationPrefixes("/app");
        }
    
        @Override
        public void registerStompEndpoints(StompEndpointRegistry registry) {
             registry.addEndpoint("/chat");
             registry.addEndpoint("/chat").withSockJS();
        }
    }
    

Here can we see that the method _configureMessageBroker_ is used to
**configure the message broker**. First, we enable an in-memory message broker
to carry the messages back to the client on destinations prefixed with
"/topic".

We complete our simple configuration by designating the "/app" prefix to
filter destinations targeting application annotated methods (via
_@MessageMapping_ ).

The _registerStompEndpoints_ method registers the  "/chat" endpoint, enabling
**Spring’s[STOMP](http://stomp.github.io/stomp-
specification-1.2.html#Abstract) support**. Keep in mind that we are also
adding here an endpoint that works without the SockJS for the sake of
elasticity.

This endpoint, when prefixed with "/app", is the endpoint that the
_ChatController.send()_ method is mapped to handle.

It also **enables the[SockJS](https://github.com/sockjs/sockjs-protocol)
fallback options,** so that alternative messaging options may be used if
WebSockets are not available. This is useful since WebSocket is not supported
in all browsers yet and may be precluded by restrictive network proxies.

The fallbacks let the applications use a WebSocket API but gracefully degrade
to non-WebSocket alternatives when necessary at runtime.

## **4\. Create the Message Model**

Now that we’ve set up the project and configured the WebSocket capabilities,
we need to create a message to send.

The endpoint will accept messages containing the sender name and a text in a
STOMP message whose body is a _JSON_ object. The message might look like this:

    
    
    {
        "from": "John",
        "text": "Hello!"
    }
    

To model the message carrying the text, we can create a simple __ Java object
with _from_ and _text_ properties:

    
    
    public class Message {
    
        private String from;
        private String text;
    
        // getters and setters
    }
    

By default, Spring will use the _Jackson_ library to convert our model object
to and from JSON.

## **5\. Create a Message-Handling Controller**

As we've seen, Spring's approach to working with STOMP messaging is to
associate a controller method to the configured endpoint. This is made
possible through the _@MessageMapping_ annotation.

The association between the endpoint and the controller gives us the ability
to handle the message if needed:

    
    
    @MessageMapping("/chat")
    @SendTo("/topic/messages")
    public OutputMessage send(Message message) throws Exception {
        String time = new SimpleDateFormat("HH:mm").format(new Date());
        return new OutputMessage(message.getFrom(), message.getText(), time);
    }
    

For the purposes of our example, we'll create another model object named
_OutputMessage_ to represent the output message sent to the configured
destination. We populate our object with the sender and the message text taken
from the incoming message and enrich it with a timestamp.

After handling our message, we send it to the appropriate destination defined
with the _@SendTo_ annotation. All subscribers to the  " _/topic/messages_ "
destination will receive the message.

## **6\. Create a Browser Client**

After making our configurations in the server-side, we'll use the **[sockjs-
client](https://github.com/sockjs/sockjs-client) library** to build a simple
HTML page that interacts with our messaging system.

First of all, we need to import the _sockjs_ and _stomp_ Javascript client
libraries. Next, we can create a _connect()_ function to open the
communication with our endpoint, a _sendMessage()_ function to send our STOMP
message and a _disconnect()_ function to close the communication:

    
    
    <html>
        <head>
            <title>Chat WebSocket</title>
            <script src="./js/sockjs-0.3.4.js"></script>
            <script src="./js/stomp.js"></script>
            <script type="text/javascript">
                var stompClient = null;
                
                function setConnected(connected) {
                    document.getElementById('connect').disabled = connected;
                    document.getElementById('disconnect').disabled = !connected;
                    document.getElementById('conversationDiv').style.visibility 
                      = connected ? 'visible' : 'hidden';
                    document.getElementById('response').innerHTML = '';
                }
                
                function connect() {
                    var socket = new SockJS('/spring-mvc-java/chat');
                    stompClient = Stomp.over(socket);  
                    stompClient.connect({}, function(frame) {
                        setConnected(true);
                        console.log('Connected: ' + frame);
                        stompClient.subscribe('/topic/messages', function(messageOutput) {
                            showMessageOutput(JSON.parse(messageOutput.body));
                        });
                    });
                }
                
                function disconnect() {
                    if(stompClient != null) {
                        stompClient.disconnect();
                    }
                    setConnected(false);
                    console.log("Disconnected");
                }
                
                function sendMessage() {
                    var from = document.getElementById('from').value;
                    var text = document.getElementById('text').value;
                    stompClient.send("/app/chat", {}, 
                      JSON.stringify({'from':from, 'text':text}));
                }
                
                function showMessageOutput(messageOutput) {
                    var response = document.getElementById('response');
                    var p = document.createElement('p');
                    p.style.wordWrap = 'break-word';
                    p.appendChild(document.createTextNode(messageOutput.from + ": " 
                      + messageOutput.text + " (" + messageOutput.time + ")"));
                    response.appendChild(p);
                }
            </script>
        </head>
        <body onload="disconnect()">
            <div>
                <div>
                    <input type="text" id="from" placeholder="Choose a nickname"/>
                </div>
                <br />
                <div>
                    <button id="connect" onclick="connect();">Connect</button>
                    <button id="disconnect" disabled="disabled" onclick="disconnect();">
                        Disconnect
                    </button>
                </div>
                <br />
                <div id="conversationDiv">
                    <input type="text" id="text" placeholder="Write a message..."/>
                    <button id="sendMessage" onclick="sendMessage();">Send</button>
                    <p id="response"></p>
                </div>
            </div>
    
        </body>
    </html>

## **7\. Testing the Example  
**

To test our example, we can open a couple of browser windows and access the
chat page at:

    
    
    http://localhost:8080/spring-mvc-java/resources/chat.html

Once this is done, we can join the chat by entering a nickname and hitting the
connect button. If we compose and send a message we can see it in all browser
sessions that have joined the chat.

Take a look at the screenshot to see an example:  

[![screenshot](/wp-content/uploads/2016/07/screenshot.png)](/wp-
content/uploads/2016/07/screenshot.png)

## **8\. Conclusion**

In this tutorial, we have explored Spring's WebSocket support. We have seen
its server side configuration and built a simple client-side counterpart with
the use of _sockjs_ and _stomp_ Javascript libraries.

The example code can be found in the [GitHub
project](https://github.com/eugenp/tutorials/tree/master/spring-mvc-java).

### The Price of all “Learn Spring Security” course packages will permanently
increase **by $50 on the 8th of December:**

**[>>> GET ACCESS NOW](/learn-spring-security-course#table)**

Sort by:   newest | oldest | most voted

![Lisdey
Pérez](http://2.gravatar.com/avatar/21c1b3b5d90056ab965c91a8f78c1cc0?s=64&r=g)

Guest

Lisdey Pérez

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Hello+and+thanks+for+so+helpfull+post%26%238230%3B+I+dont+know+is+this+is+the+right+pl...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-9700)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Hello and thanks for so helpfull post … I dont know is this is the right place
to do this, but I need some help, I need to create a Java client that is able
to connect to a WebSocket server like the one created in this post… using
Spring + Stomp + Sockjs like this post… I mean instead the JS client a Java
client. I have tried all the post that I could find about it… but it still
dont work, can anyone help me pls?

__Vote Up 0 __Vote Down  

 __1 year 3 months ago

 __

![Eugen
Paraschiv](http://1.gravatar.com/avatar/1b2827268671d62f8556627b9623ed1e?s=64&r=g)

Guest

[Eugen Paraschiv](http://www.baeldung.com/)

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Hey+Lisdey+%26%238211%3B+sure%2C+this+is+a+good+place+to+ask+for+help.%0AThat%26%238217%3Bs+an+i...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-9704)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Hey Lisdey - sure, this is a good place to ask for help.  
That's an interesting topic - I'm adding it to the Content Calendar of the
site - so keep an eye on the RSS feed in about a month. Cheers,  
Eugen.

__Vote Up 1 __Vote Down  

 __1 year 3 months ago

 __

![Lisdey
Pérez](http://2.gravatar.com/avatar/21c1b3b5d90056ab965c91a8f78c1cc0?s=64&r=g)

Guest

Lisdey Pérez

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Thanks..+I+will+do+that%26%238230%3B%0A...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-9706)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Thanks.. I will do that …

__Vote Up 0 __Vote Down  

 __1 year 3 months ago

 __

![Andy](http://2.gravatar.com/avatar/2485ac8b138be6448cfd6ccc50e3fa34?s=64&r=g)

Guest

Andy

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Hi%2C+%0AThank+you+so+much+for+you+topic.+Could+you+please+help+write+android+client...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-9947)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Hi,

Thank you so much for you topic. Could you please help write android client? I
am really need an android client to send message to server application.

Thanks,  
Andy

__Vote Up 0 __Vote Down  

 __1 year 1 month ago

 __

![Eugen
Paraschiv](http://1.gravatar.com/avatar/1b2827268671d62f8556627b9623ed1e?s=64&r=g)

Guest

[Eugen Paraschiv](http://www.baeldung.com/)

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Hey+Andy%2C%0AUnfortunately+Android+is+a+bit+outside+the+scope+of+the+site.+It%26%238217...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-9954)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Hey Andy,  
Unfortunately Android is a bit outside the scope of the site. It 's a huge
area and I only have minimal experience with mobile development - which is why
I'm not covering it here.  
Cheers,  
Eugen.

__Vote Up 0 __Vote Down  

 __1 year 1 month ago

 __

![Matthew Concrete
Blackmon](http://0.gravatar.com/avatar/37fa90233aa685bd38663a9e9b502d50?s=64&r=g)

Guest

[Matthew Concrete Blackmon](http://www.falconcis.com)

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Any+chance+that+the+JS+client+article+has+come+out%3F%0A...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-10661)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Any chance that the JS client article has come out?

__Vote Up 0 __Vote Down  

 __10 months 18 days ago

 __

![Eugen
Paraschiv](http://1.gravatar.com/avatar/1b2827268671d62f8556627b9623ed1e?s=64&r=g)

Guest

[Eugen Paraschiv](http://www.baeldung.com/)

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=It+seems+like+authors+aren%26%238217%3Bt+picking+the+WebSocket+topics%2C+so+unfortunate...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-10664)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

It seems like authors aren 't picking the WebSocket topics, so unfortunately
not 🙂  
I might be able to put it on my own writing list, but that's going to be a
longer wait.  
In the meantime, I'm sure there are lots of writeups out there covering the
topic at least partially.  
Cheers,  
Eugen.

__Vote Up 0 __Vote Down  

 __10 months 18 days ago

 __

![Markus
Streicher](http://1.gravatar.com/avatar/4d2ef8793a94d85eed147700f083a2a2?s=64&r=g)

Guest

Markus Streicher

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Hi+%40all%2C%0Ai%26%238217%3Bve+got+a+problem+with+this+tutorial.+I+just+get+a+view+with+%26%238...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-9829)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Hi @all,

i've got a problem with this tutorial. I just get a view with "Welcome to
SockJS!".  
I'm working with Spring security and a database login, WebMvc and Thymleaf.

When i add a MVC Config for Path i got a 404 error
"localhost:8080/{project}/chat/info" not found.  
And when i add also a request mapping in ChatController i got a 500 Server
error because i don't have any template resolver. When adding a template
resolver then the 500 error is already there with same message.

Please Help!

__Vote Up 0 __Vote Down  

 __1 year 2 months ago

 __

![Eugen
Paraschiv](http://1.gravatar.com/avatar/1b2827268671d62f8556627b9623ed1e?s=64&r=g)

Guest

[Eugen Paraschiv](http://www.baeldung.com/)

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Hey+Markus%2C+can+you+open+a+PR+with+a+failing+test+on+the+project%3F+The+PR+should+...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-9906)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Hey Markus, can you open a PR with a failing test on the project? The PR
should be very simple - make one of these changes and then have a live test
hitting that URL and failing. I'd be happy to have a look. Cheers,  
Eugen.

__Vote Up 1 __Vote Down  

 __1 year 1 month ago

 __

![Rohit](http://0.gravatar.com/avatar/96a93a73832b5e036792a3cde7b7237d?s=64&r=g)

Guest

Rohit

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Hi%2C%0AI+am+getting+the+same+error.+What+to+do%3F%0APlease+help.%0A...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-10099)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Hi,  
I am getting the same error. What to do?  
Please help.

__Vote Up 0 __Vote Down  

 __1 year 1 month ago

 __

![Eugen
Paraschiv](http://1.gravatar.com/avatar/1b2827268671d62f8556627b9623ed1e?s=64&r=g)

Guest

[Eugen Paraschiv](http://www.baeldung.com/)

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=A+PR+is+the+way+to+go+as+well.%0A...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-10100)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

A PR is the way to go as well.

__Vote Up 0 __Vote Down  

 __1 year 1 month ago

 __

![Rohit](http://0.gravatar.com/avatar/96a93a73832b5e036792a3cde7b7237d?s=64&r=g)

Guest

Rohit

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=Sorry%2C+What+is+a+PR%3F%0A...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-10102)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

Sorry, What is a PR?

__Vote Up 0 __Vote Down  

 __1 year 1 month ago

![Eugen
Paraschiv](http://1.gravatar.com/avatar/1b2827268671d62f8556627b9623ed1e?s=64&r=g)

Guest

[Eugen Paraschiv](http://www.baeldung.com/)

 __[ __Share On
Twitter](https://twitter.com/intent/tweet?text=No+worries%2C+sorry+for+using+jargon+like+that.+It%26%238217%3Bs+a+Pull+Request+over+on...+&url=http%3A%2F%2Fwww.baeldung.com%2Fwebsockets-
spring%2F%23comment-10103)[ __Share On
Google](https://plus.google.com/share?url=http://www.baeldung.com/websockets-
spring) ___

No worries, sorry for using jargon like that. It 's a Pull Request over on
Github.

__Vote Up 0 __Vote Down  

 __1 year 1 month ago

![wpDiscuz](http://www.baeldung.com/wp-
content/plugins/wpdiscuz/assets/img/loading.gif)

![Baeldung Logo](http://www.baeldung.com/wp-
content/themes/baeldung/icon/logo.byline.svg)

#### Categories

  * [Spring](http://www.baeldung.com/category/spring/)
  * [REST](http://www.baeldung.com/category/rest/)
  * [Java](http://www.baeldung.com/category/java/)
  * [Security](http://www.baeldung.com/category/security-2/)
  * [Persistence](http://www.baeldung.com/category/persistence/)
  * [Jackson](http://www.baeldung.com/category/jackson/)
  * [HttpClient](http://www.baeldung.com/category/http/)

#### Series

  * [Java "Back to Basics" Tutorial](http://www.baeldung.com/java-tutorial)
  * [Jackson JSON Tutorial](http://www.baeldung.com/jackson)
  * [HttpClient 4 Tutorial](http://www.baeldung.com/httpclient-guide)
  * [REST with Spring Tutorial](http://www.baeldung.com/rest-with-spring-series/)
  * [Spring Persistence Tutorial](http://www.baeldung.com/persistence-with-spring-series/)
  * [Security with Spring](http://www.baeldung.com/security-spring)

#### About

  * [About Baeldung](http://www.baeldung.com/about/)
  * [The Courses](http://courses.baeldung.com)
  * [Meta Baeldung](http://meta.baeldung.com/)
  * [The Full Archive](http://www.baeldung.com/full_archive)
  * [Write for Baeldung](http://www.baeldung.com/contribution-guidelines)
  * [Privacy Policy](http://www.baeldung.com/privacy-policy)
  * [Terms of Service](http://www.baeldung.com/terms-of-service)
  * [Contact](http://www.baeldung.com/contact)
  * [Company Info](http://www.baeldung.com/baeldung-company-info)
  * [Advertise on the Java Weekly](http://www.baeldung.com/java-weekly-sponsorship)
  * [Consulting Work](http://www.baeldung.com/consulting "My Consulting Engagements")

![Baeldung Logo](http://www.baeldung.com/wp-
content/themes/baeldung/icon/whiteleaf.svg)

