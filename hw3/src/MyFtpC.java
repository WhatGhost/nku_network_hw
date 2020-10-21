/*
 * - 计算机网络第三次作业
 * - 高钰洋 2120190419
 * - FTP客户端
 * - FTP类MyFtpC
 * */

package ftphw;
import java.io.IOException;
import java.awt.List;
import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.util.ArrayList;
import java.util.StringTokenizer;



import ftphw.GUI;
import ftphw.Files;

public class MyFtpC {
	private Socket socket = null;
	private BufferedReader reader = null;
	
	private BufferedWriter writer = null;
	
	private static boolean debug = false;


	private void sendLine(String line) throws Exception{
		if(socket == null) {
			throw new Exception("not connect!");
		}
		writer.write(line + "\r\n");
		writer.flush();
		if(debug) {
			System.out.println(">" + line);
		}
	}
	
	
	private String readLine() throws IOException {
		String line = reader.readLine();
		if(debug) {
			System.out.println("<" + line);
		}
		return line;
	}

	public synchronized boolean connect(String host, int port, String user, String pass) throws Exception {

		socket = new Socket(host, port);
		reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
		writer = new BufferedWriter(new OutputStreamWriter(socket.getOutputStream()));
		String response = readLine();
		System.out.println(response);
		if(!response.startsWith("220")) {
			return false;
		}
		sendLine("USER " + user);
		response = readLine();
		System.out.println(response);
		if(!response.startsWith("331")) {
			return false;
		}
		sendLine("PASS " + pass);
		response = readLine();
		System.out.println(response);
		if(!response.startsWith("230")) {
			return false;
		}
		System.out.println("login!");
		return true;
	}

	public synchronized String getCurrentPath() throws Exception {
		sendLine("PWD");
		String dir = null;
		String response = readLine();
		System.out.println(response);
		if(response.startsWith("257")) {
			int firstQuote = response.indexOf("\"");
			int secondQuote = response.indexOf("\"", firstQuote + 1);
			if(secondQuote > 0) {
				dir = response.substring(firstQuote + 1, secondQuote);
			}
		}
		return dir;
	}

	public synchronized boolean upload(InputStream inputStream, String fileName) throws Exception {
		BufferedInputStream input = new BufferedInputStream(inputStream);
		sendLine("PASV");
		String response = readLine();
		if(!response.startsWith("227")) {
			throw new Exception("not request passive mode!");
		}
		System.out.println("pasv"+response);
		String ip = null;
		int port = -1;
		int opening = response.indexOf('(');
		int closing = response.indexOf(')', opening + 1);
		if(closing > 0) {
			String dataLink = response.substring(opening + 1, closing);
			StringTokenizer tokenzier = new StringTokenizer(dataLink, ",");
			try {
				ip = tokenzier.nextToken() + "." + tokenzier.nextToken() + "." 
						+  tokenzier.nextToken() + "." + tokenzier.nextToken();
				port = Integer.parseInt(tokenzier.nextToken()) * 256 +Integer.parseInt(tokenzier.nextToken());;
			} catch (Exception e) {
				// TODO Auto-generated catch block
				throw new Exception("bad data link after upload!");
			}
		}
		sendLine("STOR " + fileName);
		Socket dataSocket = new Socket(ip, port);
		response = readLine();
		System.out.println(response);

		BufferedOutputStream output = new BufferedOutputStream(dataSocket.getOutputStream());
		byte[] buffer = new byte[4096];
		int bytesRead = 0;
		while((bytesRead = input.read(buffer)) != -1) {
			output.write(buffer, 0, bytesRead);
		}
		output.flush();
		output.close();
		input.close();
		response = readLine();
		System.out.println(response);
		return response.startsWith("226");
	}
	
	public synchronized ArrayList<Files> list(String path) throws Exception{
		sendLine("PASV");
		String response = readLine();
		System.out.println("pasv "+response);
		if(!response.startsWith("227")) {
			throw new Exception("not allowed to send the file!");
		}
		String ip = null;
		int port = -1;
		int opening = response.indexOf('(');
		int closing = response.indexOf(')', opening + 1);
		if(closing > 0) {
			String dataLink = response.substring(opening + 1, closing);
			StringTokenizer tokenzier = new StringTokenizer(dataLink, ",");
			try {
				ip = tokenzier.nextToken() + "." + tokenzier.nextToken() + "." 
						+  tokenzier.nextToken() + "." + tokenzier.nextToken();
				port = Integer.parseInt(tokenzier.nextToken()) * 256 +Integer.parseInt(tokenzier.nextToken());;
			} catch (Exception e) {
				// TODO Auto-generated catch block
				throw new Exception("bad data link after upload!");
			}
		}
		sendLine("LIST "+path);
		response = readLine();
		System.out.println("list "+response);
		
		Socket dataSocket = new Socket(ip, port);
		BufferedReader dataReader = new BufferedReader(new InputStreamReader(dataSocket.getInputStream()));
		String s="";
		String tmp = "";
		ArrayList<Files> alf = new ArrayList<Files>();
		while((s=dataReader.readLine())!=null) {
			tmp+=("\n"+s);
			String[] info = s.split("\\s+");
//			System.out.println(info[0]);
//			System.out.println(info[1]);
//			System.out.println(info[2]);
//			System.out.println(info[3]);
			if (info.length>4){
				for(int j=4;j<info.length;j++) {
					info[3]+=" "+info[j];
				}
			}
			Files tmpf = null;
			if(info[2].indexOf("<")!=-1) {
				tmpf = new Files(info[2], info[3], info[0]+" "+info[1], "    ");
			}
			else
				tmpf = new Files("    ", info[3], info[0]+" "+info[1],info[2]);
			alf.add(tmpf);
			
		}
		dataReader.close();
		System.out.println(tmp);
		dataSocket.close();
		response = readLine();
		System.out.println("list "+response);
		if(!response.startsWith("226")) {
			throw new Exception("not allowed to send the file!");
		}
		
		return alf;
		
	}
		
	
	public synchronized boolean download(String destFile,String srcFile) throws Exception{
		FileOutputStream output = new FileOutputStream(destFile);
		sendLine("PASV");
		String response = readLine();
		if(!response.startsWith("227")) {
			throw new Exception("not request passive mode!");
		}
		System.out.println("pasv"+response);
		String ip = null;
		int port = -1;
		int opening = response.indexOf('(');
		int closing = response.indexOf(')', opening + 1);
		if(closing > 0) {
			String dataLink = response.substring(opening + 1, closing);
			StringTokenizer tokenzier = new StringTokenizer(dataLink, ",");
			try {
				ip = tokenzier.nextToken() + "." + tokenzier.nextToken() + "." 
						+  tokenzier.nextToken() + "." + tokenzier.nextToken();
				port = Integer.parseInt(tokenzier.nextToken()) * 256 +Integer.parseInt(tokenzier.nextToken());;
			} catch (Exception e) {
				// TODO Auto-generated catch block
				throw new Exception("bad data link after upload!");
			}
		}
		sendLine("RETR " + srcFile);
		
		response = readLine();
		
		System.out.println(response);
		if(!response.startsWith("150")) {
			throw new Exception("not allowed to send the file!");
		}
		Socket dataSocket = new Socket(ip, port);
		BufferedReader dataReader = new BufferedReader(new InputStreamReader(dataSocket.getInputStream()));
		String s="";
		String tmp = "";
		while((s=dataReader.readLine())!=null) {
			tmp+=(s+"\n");
		}
		dataReader.close();
		System.out.println(tmp);
		dataSocket.close();
		response = readLine();
		System.out.println("retr "+response);

		try {
			byte[] b=tmp.getBytes();
			output.write(b);
			output.flush();
			output.close();
		}catch (Exception e) {
			// TODO: handle exception
			e.printStackTrace();
			return false;
		}
		return true;
		
		
	}
	
	public synchronized void quit() throws Exception {
		sendLine("QUIT");
		String response = readLine();
		System.out.println(response);
		socket=null;

	}
	
	public synchronized void mkdir(String folderName) throws Exception {
		sendLine("MKD "+folderName);
		String response = readLine();
		System.out.println(response);
		
		if(response.startsWith("550")) {
			System.err.println("folder already exit");
		}

	}
	
	public synchronized int delete(String fileName) throws Exception {
		sendLine("DELE "+fileName);
		String response = readLine();
		System.out.println("dele "+response);
		
		if(response.startsWith("250")) {
			return 1;
		}
		return 0;

	}
	
	public synchronized int deletefolder(String folderName) throws Exception {
		sendLine("RMD "+folderName);
		String response = readLine();
		System.out.println("RMD "+response);
		
		if(response.startsWith("250")) {
			return 1;
		}
		if(response.startsWith("257")) {
			return 1;
		}
		return 0;
	}
	
	public synchronized void cd(String folderName) throws Exception {
		sendLine("CWD "+folderName);
		String response = readLine();
		System.out.println("CWD "+response);
		

	}
	
	
	

}
