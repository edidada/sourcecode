import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.DefaultConsumer;
import com.rabbitmq.client.Envelope;
import com.rabbitmq.client.AMQP.BasicProperties;
import org.json.JSONObject;

public class Server
{
  private Connection connection;
  private Channel channel;

  public Server Server(){
    return this;
  }

  public Server init()
  throws Exception {
    ConnectionFactory factory = new ConnectionFactory();
    factory.setUsername("rpc_user");
    factory.setPassword("rpcme");
    factory.setHost("172.18.176.57");
    connection = factory.newConnection();
    channel = connection.createChannel();

    channel.exchangeDeclare("rpc", "direct");
    channel.queueDeclare("ping", false, false, false, null);
    channel.queueBind("ping", "rpc", "ping");

    channel.basicConsume("ping", false, "ping", new DefaultConsumer(channel) {
      @Override
      public void handleDelivery(String consumerTag, Envelope envelope, BasicProperties props, byte[] body) {
        try {
          channel.basicAck(envelope.getDeliveryTag(), false);
          System.out.println("Received API call...replying...");
          channel.basicPublish("", props.getReplyTo(), null, getResponse(body).getBytes("UTF-8"));
        } catch (Exception e) {
          System.out.println(e.toString());
        }
      }
    });

    System.out.println("Waiting for RPC calls...");

    return this;
  }

  public void closeConnection() {
    if (connection != null) {
      try {
        connection.close();
      }
      catch (Exception ignore) {}
    }
  }

  public void serveRequests() {
    while (true) {
      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        System.out.println(e.toString());
      }
    }
  }

  private String getResponse(byte[] body) {
    String response = null;
    try {
      String message = new String(body, "UTF-8");
      JSONObject jsonobject = new JSONObject(message);
      response = "Pong!" + jsonobject.getString("time");
    }
    catch (Exception e){
      System.out.println(e.toString());
      response = "";
    }
    return response;
  }

  public static void main(String[] args) {
    Server server = null;
    try {
      server = new Server();
      server.init().serveRequests();
    } catch(Exception e) {
      e.printStackTrace();
    } finally {
      if(server != null) {
        server.closeConnection();
      }
    }
  }
}