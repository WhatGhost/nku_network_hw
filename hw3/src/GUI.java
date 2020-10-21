/*
 * - 计算机网络第三次作业
 * - 高钰洋 2120190419
 * - FTP客户端
 * - GUI类，文件类File以及main函数
 * */

package ftphw;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.File;
import java.io.FileInputStream;
import java.util.ArrayList;

import javax.swing.*;
import javax.swing.border.Border;
import javax.xml.ws.handler.MessageContext.Scope;
import ftphw.*;


public class GUI {
	public JFrame frame;
	MyFtpC ftp;
	String currentPath;
	public GUI() {
		ftp = new MyFtpC();
		JFrame.setDefaultLookAndFeelDecorated(true);
		frame = new JFrame("FTP Client 高钰洋 2120190419");
//		frame.pack();
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setBounds(100, 100, 850, 620);
//		frame.pack();
		
		
		JPanel panel =new JPanel();
		frame.setContentPane(panel);
		panel.setBackground(new Color(255,255,0));
		panel.setLayout(new BorderLayout());
//		Box mainBox = Box.createVerticalBox();
		
		JPanel panel1 =new JPanel();
		
		panel.add(panel1,BorderLayout.NORTH);
		JPanel panel2 =new JPanel();
		panel.add(panel2,BorderLayout.CENTER);
		
		panel1.setLayout(new GridLayout(3,0));
		
		JPanel panelIpPort = new JPanel();
		JPanel panelUserPass = new JPanel();
		panel1.add(panelIpPort);
		panel1.add(panelUserPass);
		

//		panel2.setBounds(200,0,600,550);
		panel2.setBackground(new Color(255));
		
//		mainBox.add(panel1);
//		mainBox.add(Box.createHorizontalStrut(100));
//		mainBox.add(panel2);
//		panel.add(mainBox);
		
		
		Box boxIpPort = Box.createHorizontalBox();
		JLabel ipLabel = new JLabel(" 地址   ");
		boxIpPort.add(ipLabel);
		JTextField ipTextField = new JTextField(20);
		boxIpPort.add(ipTextField);
		boxIpPort.add(Box.createHorizontalStrut(5));
		JLabel portLabel = new JLabel(" 端口 ");
		boxIpPort.add(portLabel);
		JTextField portTextField = new JTextField(20);
		boxIpPort.add(portTextField);
		boxIpPort.add(Box.createHorizontalStrut(15));
		JButton btnConnect = new JButton("连接");
		boxIpPort.add(btnConnect);
		panelIpPort.add(boxIpPort);
		
		Box boxUserPass = Box.createHorizontalBox();
		JLabel userLabel = new JLabel("用户名 ");
		boxUserPass.add(userLabel);
		JTextField userTextField = new JTextField(20);
		boxUserPass.add(userTextField);
		boxUserPass.add(Box.createHorizontalStrut(5));
		JLabel passLabel = new JLabel("密码 ");
		boxUserPass.add(passLabel);
		JPasswordField passTextField = new JPasswordField(20);
		boxUserPass.add(passTextField);
		boxUserPass.add(Box.createHorizontalStrut(15));
		JButton btnQuit = new JButton("断开");
		boxUserPass.add(btnQuit);
		panelUserPass.add(boxUserPass);
		
		JLabel dirLabel = new JLabel(String.format("%50s", "未登录"));
		panel1.add(dirLabel);
		
		
		panel2.setLayout(new BorderLayout());
		JScrollPane panelList = new JScrollPane();

		JPanel panelBtn = new JPanel();
		panel2.add(panelList,BorderLayout.CENTER);
		panel2.add(panelBtn,BorderLayout.EAST);
		panel2.setBounds(0, 200, 550, 700);
		
		
		JList<Files> fileList = new JList<Files>();

		DefaultListModel<Files> dml = new DefaultListModel<Files>();
		Files ff = new Files(" ","File Name","Modification time","Size");
		
		dml.addElement(ff);

		fileList.setModel(dml);
		panelList.setViewportView(fileList);
		Font tmpf = fileList.getFont();
		Font newf = new Font("宋体",tmpf.getStyle(),tmpf.getSize()+4);
		fileList.setFont(newf);
		
		
		JButton btnUpload =		new JButton("  上  传   ");
		JButton btnDownload =	new JButton("  下  载    ");
		JButton btnDelete =		new JButton(" 删除文件 ");
		JButton btnDeleteFolder =		new JButton("删除文件夹");
		JButton btnMkdir =		new JButton("新建文件夹");
		JButton btnReFresh =	new JButton("刷新");
		JButton btnReTurn =	new JButton("返回上层目录");
		panelBtn.setLayout(new GridLayout(7,1,10,20));
		
		btnUpload.setEnabled(false);
		btnDownload.setEnabled(false);
		btnDelete.setEnabled(false);
		btnMkdir.setEnabled(false);
		btnReFresh.setEnabled(false);
		btnQuit.setEnabled(false);
		btnReTurn.setEnabled(false);
		btnDeleteFolder.setEnabled(false);
		
		panelBtn.add(btnUpload);
		panelBtn.add(btnDownload);
		panelBtn.add(btnMkdir);
		panelBtn.add(btnDelete);
		panelBtn.add(btnDeleteFolder);
		panelBtn.add(btnReTurn);
		panelBtn.add(btnReFresh);
		
		
//		panelList.setBounds(0, 200, 550, 700);
		
		
		panelIpPort.setBackground(new Color(120,255,255));
		panelUserPass.setBackground(new Color(120,255,255));
		panel1.setBackground(new Color(120,255,155));
		
		panelBtn.setBackground(new Color(255,255,155));
		
		
		fileList.setBackground(Color.WHITE);
		
		btnConnect.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				System.out.println("connet");
				String host = ipTextField.getText();
				System.out.println(host);
				String port = portTextField.getText();
				System.out.println(port);
				String user = userTextField.getText();
				System.out.println(user);
				String pass = new String(passTextField.getPassword());
				System.out.println(pass);
//				host = "192.168.1.159";
//				port="9999";
//				user="ftpuser";
//				pass="ftpuser";
				try {
					if(ftp.connect(host, Integer.parseInt(port), user, pass)) {
						infoDialog("登陆成功");
						btnUpload.setEnabled(true);
						btnDownload.setEnabled(true);
						btnDelete.setEnabled(true);
						btnMkdir.setEnabled(true);
						btnReFresh.setEnabled(true);
						btnQuit.setEnabled(true);
						btnDeleteFolder.setEnabled(true);
						btnReTurn.setEnabled(true);
						btnConnect.setEnabled(false);
						refreshList(ftp,dirLabel,fileList);
						
						
						
					}else {
						infoDialog("请输入正确的地址及用户信息！");
					}
				} catch (NumberFormatException e1) {
					// TODO Auto-generated catch block
					infoDialog("请输入正确的地址及用户信息！");
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
					infoDialog("请输入正确的地址及用户信息！");
				}
			}
		});
		btnQuit.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				System.out.println("quit");
				try {
					ftp.quit();
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
				btnUpload.setEnabled(false);
				btnDownload.setEnabled(false);
				btnDelete.setEnabled(false);
				btnMkdir.setEnabled(false);
				btnReFresh.setEnabled(false);
				btnQuit.setEnabled(false);
				btnDeleteFolder.setEnabled(false);
				btnReTurn.setEnabled(false);
				btnConnect.setEnabled(true);
				dirLabel.setText(String.format("%50s", "未登录"));
				fileList.removeAll();
				DefaultListModel<Files> dml = new DefaultListModel<Files>();
				Files tmpf = new Files(" ","File Name","Modification time","Size");
				dml.addElement(tmpf);
				fileList.setModel(dml);
			}
		});
		
		btnReFresh.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				try {
					refreshList(ftp,dirLabel,fileList);
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});
		
		btnMkdir.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				String dirName = inputDialog("请输入创建的文件夹名");
				try {
					ftp.mkdir(dirName);
					refreshList(ftp, dirLabel, fileList);
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});
		btnDelete.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				Files tmpf = fileList.getSelectedValue();
				
				try {
					if(ftp.delete(tmpf.name)==1) {
						refreshList(ftp, dirLabel, fileList);
					}
					else {
						infoDialog("删除失败，删除文件夹请点击删除文件夹按钮");
					}
				}catch(NullPointerException e2) {
					infoDialog("请选择文件");
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});
		btnDeleteFolder.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				Files tmpf = fileList.getSelectedValue();
				
				try {
					if(ftp.deletefolder(tmpf.name)==1) {
						refreshList(ftp, dirLabel, fileList);
					}
					else {
						infoDialog("删除失败，删除文件请点击删除文件按钮");
					}
				}catch(NullPointerException e2) {
					infoDialog("请选择文件夹");
				}
				catch (Exception e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});

		btnUpload.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				JFileChooser fileChooser = new JFileChooser();
				int i = fileChooser.showOpenDialog(panel);
				

				if (i == JFileChooser.APPROVE_OPTION) {
					
					File selectedFile = fileChooser.getSelectedFile();
					while(true){
						try {
							System.out.println();
							ftp.upload(new FileInputStream(selectedFile),selectedFile.getName());
							refreshList(ftp, dirLabel, fileList);
							break;
						} catch (Exception e1) {
							// TODO Auto-generated catch block
							e1.printStackTrace();
						}
					}
					
				}

			}
		});
		
		btnDownload.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				JFileChooser fileChooser = new JFileChooser();
				fileChooser.setDialogTitle("请选择下载路径");
				fileChooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
				Files tmpf = fileList.getSelectedValue();
				if(fileList.isSelectionEmpty()) {
					infoDialog("请选择要下载的文件");

				}else {
					int i = fileChooser.showOpenDialog(panel);
					if (i == JFileChooser.APPROVE_OPTION) {
						File tmpDir = fileChooser.getSelectedFile();
						
						String path = currentPath+tmpf.name;
						System.out.println(path);
						String dest = tmpDir+"\\"+tmpf.name;
						System.out.println(dest);
						while(true) {
							try {
								ftp.download(dest, path);
								refreshList(ftp, dirLabel, fileList);
								break;
							} catch (Exception e1) {
								// TODO Auto-generated catch block
								e1.printStackTrace();
							}
						}
					}
				}
				
			}
		});
		
		fileList.addMouseListener(new MouseListener() {
			
			@Override
			public void mouseClicked(MouseEvent arg0) {
				// TODO Auto-generated method stub
				if(arg0.getClickCount()==2) {
					Files tmpf = fileList.getSelectedValue();
					if(tmpf.isdir.indexOf('<')!=-1) {
						try {
							ftp.cd(tmpf.name);
							refreshList(ftp, dirLabel, fileList);
						} catch (Exception e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
					}
				}
			}
			@Override
			public void mouseEntered(MouseEvent e) {
				// TODO Auto-generated method stub			
			}
			@Override
			public void mouseExited(MouseEvent e) {
				// TODO Auto-generated method stub		
			}
			@Override
			public void mousePressed(MouseEvent e) {
				// TODO Auto-generated method stub
				
			}
			@Override
			public void mouseReleased(MouseEvent e) {
				// TODO Auto-generated method stub
				
			}
		});
		
		btnReTurn.addActionListener(new ActionListener() {
			
			@Override
			public void actionPerformed(ActionEvent e) {
				// TODO Auto-generated method stub
				if(currentPath.equals("/")) {
					infoDialog("已经到达根目录");
				}
				try {
					ftp.cd("..");
					refreshList(ftp, dirLabel, fileList);
				} catch (Exception e1) {
					// TODO Auto-generated catch block
					e1.printStackTrace();
				}
			}
		});
		
	}
	
	public void refreshList(MyFtpC ftp,JLabel dirLabel,JList<Files> fileList) throws Exception {
		String curDir = ftp.getCurrentPath();
		dirLabel.setText("当前目录:   "+curDir);
		this.currentPath=curDir;
		ArrayList<Files> alf =  ftp.list(curDir);
		DefaultListModel<Files> dml = new DefaultListModel<Files>();
		Files tmpf = new Files(" ","File Name","Modification time","Size");
		dml.addElement(tmpf);
		for(int i=0;i<alf.size();i++) {
			dml.addElement(alf.get(i));
		}
		fileList.setModel(dml);
	}
	
	public static void infoDialog(String mesg)  
    {  
        JOptionPane.showMessageDialog(null,  
            "<html><font color=\"green\"  style=\"font-weight:bold;\" >" + mesg  
                + "</font></html>", "消息",  
            JOptionPane.INFORMATION_MESSAGE);  
    } 
	public static String inputDialog(String mesg)  
    {  
        String dirName = JOptionPane.showInputDialog(null,  
            "<html><font color=\"green\"  style=\"font-weight:bold;\" >" + mesg  
                + "</font></html>", "输入",  
            JOptionPane.INFORMATION_MESSAGE);  
        return dirName;
    }
	
	public static void main(String args[]) {
		
		try {
            for (javax.swing.UIManager.LookAndFeelInfo info : javax.swing.UIManager.getInstalledLookAndFeels()) {
                System.out.println(info.getName());
            	if ("Nimbus".equals(info.getName())) {
                    javax.swing.UIManager.setLookAndFeel(info.getClassName());
//                    break;
                }
            }
        }catch(Exception e) {
        	System.out.println(e);
        }

		
		GUI gui = new GUI();
		gui.frame.setVisible(true);
	}
	
}


class Files {
	String isdir="null";
	String name="null";
	String modifyTime="null";
	String size="null";
	public Files(String d,String n,String m,String s) {
		// TODO Auto-generated constructor stub
		isdir=d;
		name=n;
		modifyTime=m;
		size=s;
	}
	public static String flushLeft(char c, long length, String content){             
	       String str = "";     
	       long cl = 0;    
	       String cs = "";     
	       if (content.length() > length){     
	            str = content;     
	       }else{    
	            for (int i = 0; i < length - content.length(); i++){     
	                cs = cs + c;     
	            }  
	          }  
	        str = content + cs;      
	        return str;      
	   } 
	@Override
	public String toString() {
		// TODO Auto-generated method stub
		return flushLeft(' ',8,isdir)+flushLeft(' ',30,name)+flushLeft(' ',25,modifyTime)+flushLeft(' ',10,size);
	}
}
